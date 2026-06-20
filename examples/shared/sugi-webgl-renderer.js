export class SugiWebGLRenderer {
  constructor(canvas, { baseUrl = '../../', fallback2d = true } = {}) {
    this.canvas = canvas;
    this.baseUrl = baseUrl;
    this.gl = canvas.getContext('webgl2', { premultipliedAlpha: true, alpha: true });
    this.ctx2d = !this.gl && fallback2d ? canvas.getContext('2d') : null;
    this.programs = new Map();
    this.textures = new Map();
    this.quad = null;
  }

  resize() {
    const dpr = window.devicePixelRatio || 1;
    const width = Math.max(1, Math.floor(this.canvas.clientWidth * dpr));
    const height = Math.max(1, Math.floor(this.canvas.clientHeight * dpr));
    if (this.canvas.width !== width || this.canvas.height !== height) {
      this.canvas.width = width;
      this.canvas.height = height;
    }
  }

  async loadScene(scene) {
    this.scene = scene;
    this.nodes = this.flatten(scene);
    this.root = this.nodes.find((node) => node.type === 'page') || scene[0];
    this.materials = this.root?.properties?.__materials || {};
    if (this.gl) {
      this.initQuad();
      await Promise.all(Object.entries(this.materials).map(([name, material]) => this.compileMaterial(name, material)));
    }
  }

  flatten(nodes, out = []) {
    for (const node of nodes || []) {
      out.push(node);
      this.flatten(node.children || [], out);
    }
    return out;
  }

  initQuad() {
    if (this.quad || !this.gl) return;
    const gl = this.gl;
    this.quad = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, this.quad);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, -1,1, 1,-1, 1,1]), gl.STATIC_DRAW);
  }

  async compileMaterial(name, material) {
    if (this.programs.has(name)) return this.programs.get(name);
    const [vertex, fragment] = await Promise.all([this.fetchText(material.vertex), this.fetchText(material.fragment)]);
    const program = this.linkProgram(vertex, this.convertFragment(fragment, material));
    this.programs.set(name, { program, material });
    return this.programs.get(name);
  }

  async fetchText(path) {
    const response = await fetch(this.resolve(path));
    if (!response.ok) throw new Error(`Unable to load shader ${path}: ${response.status}`);
    return response.text();
  }

  resolve(path) {
    if (/^(https?:|data:|\/)/.test(path)) return path;
    return `${this.baseUrl}${path}`;
  }

  convertFragment(source, material) {
    if (material.shadertoy) {
      return `#version 300 es\nprecision mediump float;\nin vec2 v_uv;\nout vec4 out_color;\nuniform vec3 iResolution;\nuniform float iTime;\nuniform vec4 iMouse;\n${source.replace(/#version[^\n]*\n/g, '')}\nvoid main(){ mainImage(out_color, v_uv * iResolution.xy); }`;
    }
    return source
      .replace(/#version\s+330\s+core/g, '#version 300 es\nprecision mediump float;')
      .replace(/\blayout\s*\([^)]*\)\s*in\b/g, 'in')
      .replace(/\btexture2D\s*\(/g, 'texture(');
  }

  compileShader(type, source) {
    const gl = this.gl;
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      const log = gl.getShaderInfoLog(shader);
      gl.deleteShader(shader);
      throw new Error(log || 'Shader compile failed');
    }
    return shader;
  }

  linkProgram(vertex, fragment) {
    const gl = this.gl;
    const program = gl.createProgram();
    gl.attachShader(program, this.compileShader(gl.VERTEX_SHADER, vertex));
    gl.attachShader(program, this.compileShader(gl.FRAGMENT_SHADER, fragment));
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program) || 'Program link failed');
    return program;
  }

  async textureFor(src) {
    if (!src) return null;
    if (this.textures.has(src)) return this.textures.get(src);
    const gl = this.gl;
    const texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array([255, 255, 255, 255]));
    const image = new Image();
    image.crossOrigin = 'anonymous';
    image.onload = () => { gl.bindTexture(gl.TEXTURE_2D, texture); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image); };
    image.src = this.resolve(src);
    this.textures.set(src, texture);
    return texture;
  }

  setCommonUniforms(program, rect, now) {
    const gl = this.gl;
    const set1f = (name, value) => { const loc = gl.getUniformLocation(program, name); if (loc) gl.uniform1f(loc, value); };
    const set2f = (name, a, b) => { const loc = gl.getUniformLocation(program, name); if (loc) gl.uniform2f(loc, a, b); };
    const set3f = (name, a, b, c) => { const loc = gl.getUniformLocation(program, name); if (loc) gl.uniform3f(loc, a, b, c); };
    const set4f = (name, a, b, c, d) => { const loc = gl.getUniformLocation(program, name); if (loc) gl.uniform4f(loc, a, b, c, d); };
    set1f('time', now);
    set1f('iTime', now);
    set1f('iFrame', Math.floor(now * 60));
    set2f('viewportSize', this.canvas.width, this.canvas.height);
    set3f('iResolution', rect.width, rect.height, 1);
    set4f('iMouse', 0, 0, 0, 0);
  }

  setMaterialUniforms(program, uniforms = {}) {
    const gl = this.gl;
    for (const [name, value] of Object.entries(uniforms)) {
      if (value === 'auto') continue;
      const loc = gl.getUniformLocation(program, name);
      if (!loc) continue;
      if (typeof value === 'number') gl.uniform1f(loc, value);
      else if (!Number.isNaN(Number(value))) gl.uniform1f(loc, Number(value));
      else if (Array.isArray(value) && value.length === 2) gl.uniform2f(loc, Number(value[0]), Number(value[1]));
      else if (Array.isArray(value) && value.length === 3) gl.uniform3f(loc, Number(value[0]), Number(value[1]), Number(value[2]));
      else if (Array.isArray(value) && value.length === 4) gl.uniform4f(loc, Number(value[0]), Number(value[1]), Number(value[2]), Number(value[3]));
    }
  }

  async render(now = performance.now() / 1000, cameraX = 0) {
    this.resize();
    if (!this.gl) return this.render2d(now, cameraX);
    const gl = this.gl;
    gl.viewport(0, 0, this.canvas.width, this.canvas.height);
    gl.clearColor(0.02, 0.04, 0.08, 1);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    for (const node of this.nodes) await this.drawNode(node, now, cameraX);
  }

  async drawNode(node, now, cameraX) {
    const p = node.properties || {};
    if (!['shader_surface', 'surface', 'sprite', 'image', 'platform', 'panel', 'viewport'].includes(node.type)) return;
    const materialName = p.material;
    const material = this.programs.get(materialName);
    if (material) this.drawMaterialNode(node, material, now, cameraX);
    if (p.image || p.source) await this.drawImageNode(node, p.image || p.source, now, cameraX);
    if (!material && !p.image && !p.source) this.drawColorNode(node, cameraX);
  }

  drawMaterialNode(node, entry, now, cameraX) {
    const gl = this.gl;
    const p = node.properties || {};
    const parallax = Number(p.parallax ?? 1);
    const x = Number(p.x || 0) - cameraX * parallax;
    const y = Number(p.y || 0);
    const w = Number(p.width || 0);
    const h = Number(p.height || 0);
    if (!w || !h) return;
    gl.useProgram(entry.program);
    this.bindQuad(entry.program, x, y, w, h);
    this.setCommonUniforms(entry.program, { width: w, height: h }, now);
    this.setMaterialUniforms(entry.program, entry.material.uniforms || {});
    gl.drawArrays(gl.TRIANGLES, 0, 6);
  }

  drawColorNode(node, cameraX) {
    const gl = this.gl;
    const p = node.properties || {};
    const entry = this.programs.get('__color') || this.createColorProgram();
    gl.useProgram(entry.program);
    const parallax = Number(p.parallax ?? 1);
    const x = Number(p.x || 0) - cameraX * parallax;
    const y = Number(p.y || 0);
    const w = Number(p.width || 0);
    const h = Number(p.height || 0);
    if (!w || !h) return;
    this.bindQuad(entry.program, x, y, w, h);
    const color = this.hexToRgba(p.color || '#1e293b');
    const loc = gl.getUniformLocation(entry.program, 'u_color');
    gl.uniform4f(loc, color[0], color[1], color[2], color[3]);
    gl.drawArrays(gl.TRIANGLES, 0, 6);
  }

  createColorProgram() {
    const vertex = `#version 300 es\nprecision mediump float;\nin vec2 a_position;\nout vec2 v_uv;\nuniform vec4 u_rect;\nuniform vec2 u_viewport;\nvoid main(){ v_uv = a_position * 0.5 + 0.5; vec2 pixel = u_rect.xy + v_uv * u_rect.zw; vec2 clip = pixel / u_viewport * 2.0 - 1.0; gl_Position = vec4(clip.x, -clip.y, 0.0, 1.0); }`;
    const fragment = `#version 300 es\nprecision mediump float;\nout vec4 out_color;\nuniform vec4 u_color;\nvoid main(){ out_color = u_color; }`;
    const entry = { program: this.linkProgram(vertex, fragment), material: {} };
    this.programs.set('__color', entry);
    return entry;
  }

  hexToRgba(value) {
    const hex = String(value).replace('#', '').trim();
    if (hex.length === 3) return hex.split('').map((c) => parseInt(c + c, 16) / 255).concat(1);
    if (hex.length >= 6) return [parseInt(hex.slice(0, 2), 16) / 255, parseInt(hex.slice(2, 4), 16) / 255, parseInt(hex.slice(4, 6), 16) / 255, 1];
    return [0.12, 0.16, 0.23, 1];
  }

  async drawImageNode(node, src, now, cameraX) {
    const gl = this.gl;
    const p = node.properties || {};
    const texture = await this.textureFor(src);
    const programEntry = this.programs.get('__image') || this.createImageProgram();
    gl.useProgram(programEntry.program);
    const x = Number(p.x || 0) - cameraX;
    const y = Number(p.y || 0);
    const w = Number(p.width || 0);
    const h = Number(p.height || 0);
    this.bindQuad(programEntry.program, x, y, w, h);
    const sampler = gl.getUniformLocation(programEntry.program, 'u_texture');
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.uniform1i(sampler, 0);
    gl.drawArrays(gl.TRIANGLES, 0, 6);
  }

  createImageProgram() {
    const vertex = `#version 300 es\nprecision mediump float;\nin vec2 a_position;\nout vec2 v_uv;\nuniform vec4 u_rect;\nuniform vec2 u_viewport;\nvoid main(){ vec2 pixel = u_rect.xy + (a_position * 0.5 + 0.5) * u_rect.zw; vec2 clip = pixel / u_viewport * 2.0 - 1.0; gl_Position = vec4(clip.x, -clip.y, 0.0, 1.0); v_uv = a_position * 0.5 + 0.5; }`;
    const fragment = `#version 300 es\nprecision mediump float;\nin vec2 v_uv;\nout vec4 out_color;\nuniform sampler2D u_texture;\nvoid main(){ out_color = texture(u_texture, v_uv); }`;
    const entry = { program: this.linkProgram(vertex, fragment), material: {} };
    this.programs.set('__image', entry);
    return entry;
  }

  bindQuad(program, x, y, w, h) {
    const gl = this.gl;
    const pos = gl.getAttribLocation(program, 'a_position');
    gl.bindBuffer(gl.ARRAY_BUFFER, this.quad);
    gl.enableVertexAttribArray(pos);
    gl.vertexAttribPointer(pos, 2, gl.FLOAT, false, 0, 0);
    const rect = gl.getUniformLocation(program, 'u_rect');
    const viewport = gl.getUniformLocation(program, 'u_viewport');
    if (rect && viewport) {
      gl.uniform4f(rect, x, y, w, h);
      gl.uniform2f(viewport, this.canvas.width, this.canvas.height);
    }
  }

  render2d(now, cameraX) {
    const ctx = this.ctx2d;
    if (!ctx) throw new Error('WebGL2 is unavailable and Canvas2D fallback is disabled.');
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    ctx.fillStyle = '#06111f';
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    for (const node of this.nodes) {
      const p = node.properties || {};
      if (['shader_surface', 'surface', 'sprite'].includes(node.type)) {
        const x = Number(p.x || 0) - cameraX * Number(p.parallax ?? 1);
        const y = Number(p.y || 0), w = Number(p.width || 0), h = Number(p.height || 0);
        const g = ctx.createLinearGradient(x, y, x + w, y + h);
        g.addColorStop(0, p.color || '#0284c7');
        g.addColorStop(1, '#67e8f9');
        ctx.fillStyle = g;
        ctx.fillRect(x, y, w, h);
      }
    }
  }
}
