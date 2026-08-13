import hashlib,hmac,logging
from flask import Flask, request, jsonify
from .config import Settings
from .runner import CommandRunner, DeploymentPipeline

log = logging.getLogger("cicd.webhook")
app = Flask(__name__)
settings = Settings()

def valid_signature(body, signature):
    if not signature or not signature.startswith("sha256="): return False
    expected = hmac.new(settings.webhook_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest("sha256="+expected, signature)

@app.get("/healthz")
def healthz(): return {"status":"ok"}

@app.post("/webhook")
def webhook():
    body = request.get_data()
    if not valid_signature(body, request.headers.get("X-Hub-Signature-256")):
        return jsonify(error="invalid signature"), 401
    event = request.headers.get("X-GitHub-Event")
    if event not in {"push","ping"}:
        return jsonify(status="ignored"), 202
    if event == "ping":
        return jsonify(status="pong"), 200
    try:
        result = DeploymentPipeline(CommandRunner(), settings.repo_dir, settings.compose_file).execute()
        return jsonify(result), 200
    except Exception:
        log.exception("deployment failed")
        return jsonify(error="deployment failed"), 500

if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    app.run(host="0.0.0.0", port=settings.port)
