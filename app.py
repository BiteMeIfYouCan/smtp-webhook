import yaml, logging, datetime
from flask import Flask, request, jsonify
import yagmail

# ---------- 读取配置 ----------
with open("/config/config.yaml", "r") as f:
    CONF = yaml.safe_load(f)

# ---------- 日志 ----------
logging.basicConfig(
    filename="/config/webmail.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
def log(msg: str):
    logging.info(msg)
    print(msg, flush=True)

# ---------- Flask ----------
app = Flask(__name__)

def send_mail(smtp_id: str, to: str, cc, subject: str, body: str):
    s = CONF["smtp_servers"][smtp_id]
    yag = yagmail.SMTP(
        user=s["user"],
        password=s["password"],
        host=s["host"],
        port=s["port"],
        smtp_starttls=s.get("starttls", True),
        smtp_ssl=not s.get("starttls", True),
        timeout=10,                       # 10 s 超时
    )
    yag.send(to=to, cc=cc, subject=subject, contents=[body])

@app.route("/send", methods=["POST"])
def api_send():
    data     = request.get_json(silent=True) or request.form
    token    = data.get("token")
    smtp_id  = data.get("smtp_id", "default")
    to       = data.get("to")
    cc       = data.get("cc") or None
    subject  = data.get("subject", "(no subject)")
    body     = data.get("body", "")
    ip       = request.remote_addr
    req_ts   = datetime.datetime.utcnow().isoformat(timespec="seconds")+"Z"

    # ---------- 校验 ----------
    if token not in CONF["tokens"]:
        log(f'{{"req_ts":"{req_ts}","ip":"{ip}","token":"{token}",'
            f'"smtp":"{smtp_id}","to":"{to}","subject":"{subject[:40]}",'
            f'"status":"DENY_TOKEN"}}')
        return jsonify({"error": "invalid token"}), 403

    if smtp_id not in CONF["tokens"][token]:
        return jsonify({"error": "token not allowed for this smtp_id"}), 403

    if smtp_id not in CONF["smtp_servers"]:
        return jsonify({"error": "unknown smtp_id"}), 400

    if not to:
        return jsonify({"error": "missing 'to'"}), 400

    # ---------- 发送 ----------
    try:
        send_mail(smtp_id, to, cc, subject, body)
        log(f'{{"req_ts":"{req_ts}","ip":"{ip}","token":"{token}",'
            f'"smtp":"{smtp_id}","to":"{to}","subject":"{subject[:40]}",'
            f'"status":"OK"}}')
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        log(f'{{"req_ts":"{req_ts}","ip":"{ip}","token":"{token}",'
            f'"smtp":"{smtp_id}","to":"{to}","subject":"{subject[:40]}",'
            f'"status":"ERROR","detail":"{e}"}}')
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 关闭 reloader，避免双进程
    app.run(host="0.0.0.0", port=8080, use_reloader=False)
