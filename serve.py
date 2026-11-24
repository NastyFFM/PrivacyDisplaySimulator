# HTTPS server for testing on phones in the local Wi-Fi.
# Phones only expose gyroscope data on HTTPS, hence the self-signed cert.
# ponytail: self-signed → browser warning on first visit; use mkcert or a real host if that annoys.
import http.server, ssl, socket, subprocess, os

PORT = 8443
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if not os.path.exists(".cert/cert.pem"):
    os.makedirs(".cert", exist_ok=True)
    subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "365",
                    "-keyout", ".cert/key.pem", "-out", ".cert/cert.pem", "-subj", "/CN=privacy-sim"],
                   check=True, capture_output=True)

# macOS Wi-Fi is en0; the socket trick would pick a VPN interface if one is up.
ip = subprocess.run(["ipconfig", "getifaddr", "en0"], capture_output=True, text=True).stdout.strip()
if not ip:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("10.255.255.255", 1))  # no packet sent, just picks the default interface
    ip = s.getsockname()[0]

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain(".cert/cert.pem", ".cert/key.pem")
httpd = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), http.server.SimpleHTTPRequestHandler)
httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
print(f"Open on your phone:https://{ip}:{PORT}", flush=True)
httpd.serve_forever()
