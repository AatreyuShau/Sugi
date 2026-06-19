# Canvas Login Demo

This demo keeps the browser intentionally thin: `web/index.html` owns a single canvas and forwards mouse/keyboard events to Python. The Python server compiles `login.yaml`, owns focus/input/login logic, mutates the SUGI VM DOM, and returns draw commands for the canvas to render.

## Run

From the repository root:

```bash
python examples/login_canvas/server/login_server.py
```

Open <http://localhost:8765>.

Credentials:

- Username: `demo`
- Password: `sugi`

## Test

```bash
pytest -q tests/test_login_canvas_demo.py
```

## Showcase coverage

The login demo exercises input nodes, text rendering, focus variables, protocol-style browser event relay, and server-owned VM mutations while the browser only executes draw commands.
