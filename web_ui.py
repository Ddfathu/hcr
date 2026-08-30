import os
import subprocess
import signal
from flask import Flask, request, render_template_string

app = Flask(__name__)

CONFIG = {
    "port": os.getenv("PORT", "8080"),
    "max_frame": "4096",
    "timeout": "8s",
    "transport": "plain", # "plain" atau "tls"
    "ssh_user": "root",
    "ssh_pass": os.getenv("SSH_PASS", "PasswordHCR123")
}

hcr_proc = None

def generate_self_signed_cert():
    cert_path = "/app/certs/cert.pem"
    key_path = "/app/certs/key.pem"
    # Buat sertifikat dengan CN & SAN altaria.proxy.rlwy.net
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-keyout", key_path, "-out", cert_path,
            "-days", "365", "-nodes",
            "-subj", "/CN=altaria.proxy.rlwy.net",
            "-addext", "subjectAltName=DNS:altaria.proxy.rlwy.net,DNS:*.proxy.rlwy.net"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return cert_path, key_path

def update_ssh_credentials(user, password):
    check_user = subprocess.run(["id", user], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if check_user.returncode != 0:
        subprocess.run(["useradd", "-m", "-s", "/bin/bash", user])
    subprocess.run(["sh", "-c", f"echo '{user}:{password}' | chpasswd"])
    CONFIG["ssh_user"] = user
    CONFIG["ssh_pass"] = password

def run_hcr(frame, timeout, transport):
    global hcr_proc
    if hcr_proc:
        try:
            hcr_proc.send_signal(signal.SIGTERM)
            hcr_proc.wait(timeout=2)
        except Exception:
            hcr_proc.kill()
    
    cmd = [
        "/app/hcr-server",
        "--listen", f":{CONFIG['port']}",
        "--target", "127.0.0.1:22",
        "--transport", transport,
        "--max-download-frame", str(frame),
        "--download-poll-timeout", str(timeout)
    ]

    if transport == "tls":
        cert, key = generate_self_signed_cert()
        cmd.extend(["--cert-file", cert, "--key-file", key])

    hcr_proc = subprocess.Popen(cmd)
    CONFIG["max_frame"] = str(frame)
    CONFIG["timeout"] = str(timeout)
    CONFIG["transport"] = transport

HTML_PAGE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>HCR Server & SSH Manager</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 15px; margin: 0; }
        .card { max-width: 440px; margin: auto; background: #1e293b; padding: 24px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); }
        h2 { margin-top: 0; font-size: 20px; color: #38bdf8; text-align: center; }
        label { font-size: 13px; font-weight: 600; color: #94a3b8; display: block; margin-top: 12px; }
        select, input, button { width: 100%; padding: 10px; margin-top: 6px; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        select, input { background: #0f172a; color: #f8fafc; border: 1px solid #334155; }
        select:focus, input:focus { border-color: #38bdf8; outline: none; }
        button { background: #0284c7; color: white; font-weight: bold; border: none; cursor: pointer; margin-top: 20px; padding: 12px; }
        button:hover { background: #0369a1; }
        .status { padding: 10px; background: #065f46; color: #34d399; border-radius: 6px; margin-bottom: 15px; font-size: 13px; text-align: center; }
        .divider { border-top: 1px solid #334155; margin: 18px 0 6px 0; }
        .toggle-box { display: flex; align-items: center; justify-content: space-between; margin-top: 10px; background: #0f172a; padding: 10px; border-radius: 6px; border: 1px solid #334155; }
        .toggle-box input[type="checkbox"] { width: auto; margin: 0; transform: scale(1.3); cursor: pointer; }
    </style>
</head>
<body>
<div class="card">
    <h2>HCR & SSH Manager</h2>
    {% if msg %}<div class="status">{{ msg }}</div>{% endif %}

    <form method="POST">
        <div style="font-weight: bold; color: #e2e8f0; margin-bottom: 4px;">Konfigurasi Akun SSH</div>
        
        <label>SSH Username:</label>
        <input type="text" name="ssh_user" value="{{ conf.ssh_user }}" required>

        <label>SSH Password:</label>
        <input type="text" name="ssh_pass" value="{{ conf.ssh_pass }}" required>

        <div class="divider"></div>
        <div style="font-weight: bold; color: #e2e8f0; margin-bottom: 4px;">Tuning Protokol HCR</div>

        <div class="toggle-box">
            <span style="font-size: 14px; font-weight: 600;">Aktifkan Server TLS (HTTPS)</span>
            <input type="checkbox" name="transport_tls" value="yes" {% if conf.transport=='tls' %}checked{% endif %}>
        </div>

        <label>Max Download Frame:</label>
        <select id="frame_sel" onchange="if(this.value!='custom') document.getElementById('frame_custom').value=this.value;">
            <option value="1024" {% if conf.max_frame=='1024' %}selected{% endif %}>1024 (1 KB - Ringan)</option>
            <option value="2048" {% if conf.max_frame=='2048' %}selected{% endif %}>2048 (2 KB)</option>
            <option value="4096" {% if conf.max_frame=='4096' %}selected{% endif %}>4096 (4 KB - Standar)</option>
            <option value="6144" {% if conf.max_frame=='6144' %}selected{% endif %}>6144 (6 KB - Bawaan)</option>
            <option value="8192" {% if conf.max_frame=='8192' %}selected{% endif %}>8192 (8 KB - Kencang)</option>
            <option value="custom">Custom Angka...</option>
        </select>
        <input type="text" id="frame_custom" name="max_frame" value="{{ conf.max_frame }}" placeholder="Isi angka frame (byte)">

        <label>Download Poll Timeout:</label>
        <select id="timeout_sel" onchange="if(this.value!='custom') document.getElementById('timeout_custom').value=this.value;">
            <option value="1s" {% if conf.timeout=='1s' %}selected{% endif %}>1s (Agresif / Low Ping)</option>
            <option value="2s" {% if conf.timeout=='2s' %}selected{% endif %}>2s</option>
            <option value="4s" {% if conf.timeout=='4s' %}selected{% endif %}>4s</option>
            <option value="8s" {% if conf.timeout=='8s' %}selected{% endif %}>8s (Stabil Bawaan)</option>
            <option value="10s" {% if conf.timeout=='10s' %}selected{% endif %}>10s</option>
            <option value="custom">Custom Format...</option>
        </select>
        <input type="text" id="timeout_custom" name="timeout" value="{{ conf.timeout }}" placeholder="Contoh: 3s atau 5s">

        <button type="submit">Simpan & Terapkan Perubahan</button>
    </form>
</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    msg = None
    if request.method == "POST":
        frame = request.form.get("max_frame", "4096").strip()
        timeout = request.form.get("timeout", "8s").strip()
        user = request.form.get("ssh_user", "root").strip()
        password = request.form.get("ssh_pass", "PasswordHCR123").strip()
        transport = "tls" if request.form.get("transport_tls") == "yes" else "plain"
        
        update_ssh_credentials(user, password)
        run_hcr(frame, timeout, transport)
        
        msg = f"Tersimpan! Akun: {user} | Mode: {transport.upper()} | Frame: {frame} | Timeout: {timeout}"
    return render_template_string(HTML_PAGE, conf=CONFIG, msg=msg)

if __name__ == "__main__":
    update_ssh_credentials(CONFIG["ssh_user"], CONFIG["ssh_pass"])
    run_hcr(CONFIG["max_frame"], CONFIG["timeout"], CONFIG["transport"])
    app.run(host="0.0.0.0", port=8081)
