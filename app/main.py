"""Trade Validation Service - demo app for BNP Paribas CIB SDLC walkthrough."""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

ENVIRONMENT = os.getenv("APP_ENV", "local")
VERSION = os.getenv("APP_VERSION", "dev")
SUPPORTED_CCY = {"EUR", "USD", "GBP", "JPY", "CHF"}
MAX_NOTIONAL = 50_000_000


def validate_trade(trade: dict) -> list[str]:
    errors = []
    if trade.get("currency") not in SUPPORTED_CCY:
        errors.append("unsupported currency")
    notional = trade.get("notional", 0)
    if not isinstance(notional, (int, float)) or notional <= 0:
        errors.append("notional must be positive")
    elif notional > MAX_NOTIONAL:
        errors.append("notional exceeds limit")
    if trade.get("side") not in {"BUY", "SELL"}:
        errors.append("side must be BUY or SELL")
    return errors


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "ok", "env": ENVIRONMENT, "version": VERSION})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/validate":
            return self._send(404, {"error": "not found"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            trade = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            return self._send(400, {"error": "invalid json"})
        errors = validate_trade(trade)
        self._send(200 if not errors else 422, {"valid": not errors, "errors": errors})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
