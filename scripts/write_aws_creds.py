import json
import os

# Use a raw string for the private key to prevent escaping issues
pk = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDMKMZukPNOBEIV
gg3+JOqjnnL1wyJP1BYtWpBNrDTCmovQiPJlx6mqdHao0NRtm6/1z/dIBJ2CmcfZ
rXJwQd20qbTGCBq9vHFS0BiBOxIMq+EPmsdyBGeXL/pKNheuxCqN1D6Xh1FZyVFU
+WtZF2LPlICwjLiSIzkKHE/HOVE2DxiQFr1mLekKTrChKiCU3sYL3UiprG//va0n
6vXCyehLmfrmBh2sepyMR2HmowjpzH5/iQhitwi2i/U+3m3VHSoNLNRTMlQmZ5xp
2zux81O2PxhUwkHAkkYHBxT5noQPnZt1tAihXB/2QChhKoReOVL8DYPVRK2gAyJ0
3UW2AbSjAgMBAAECggEAA7r9ATkx0Ouf/3+cXNf015+GDzqNDnNcImEEwP6UCjhD
tMBD2Zs/3Ob64hPKxePx36Z4qL642BGSRsZ2EFoLwIjXTkUIpA3k7jPyNq5LIqMj
XiMgYNN2xxrv0lpRrXZVJrlJmYA1+tOEYm6aSQr12cAnZ9Jybu0o1if1RzkjZD7z
Aw/BSrbGevjNsU8fmzRrL3+LJXk44H9Ammo+0akrDEodQelLOulXrBT0DU0bWnFK
8RNV0QNPpU8DDMUkXkDauSAF2GGNUFa7fFIFbJW3HvWX+KcZ6LN0Phpsb5H7xYT0
+U1BfhtaxiUa+BJpoNqxlzEvYmXeMrljxx6taGUptQKBgQDqCgO4JsQCCGTtP7IU
VXWgH9tfjGR9fx1h0ScQMIOnAmdL+Q7Ic6QTzaJTyXtKJEPj22YOAf+nmoVHe7Oc
kDziGE8cO3fBpo5MG7MmBudUjw2MG3MlyliKaVnYhv4cVpXx0waITPrkv4dXBykt
AWiKOAhWmJUDZOGv8ujXwOxdFQKBgQDfUQAGiXlAvd7upZjGKj3GRhDzep+g5iS1
cbvUfThQlIUxHIVbziWdSJywbKWguaM+h9vQFQLqiyhFsuEIxFj21PXh6C9cVHEi
VOOfiGKId/S+FqlPhld1zg/i+5GwMXIE3Rjcthv+ErncwDd9ySHsz9N08SsaBH3M
nnQHkRLNo1wKBgQCKz+vK0rtZFU9/ZFMkOlfs5FhCQMvtn3J27Q3FTXEYopVP+2Xo
QKal1EaeeZd1rzLRN/U9A7R13XGFp3ott2NVGuP5M9Bg/H/T5m4IdPnKLprzaeiP
FogTeE8A3XhkqHqBFw/90eLRwEPuu2GRvw8ZRAi2DAP+Ily19lZieZv3zQKBgBdr
bj5BQpcYkn2inkACBBJ8HKD8Nitwl17z+4fQTgydVs6MuCullepFyDD0Y/ZUIZuY
MeRDn9erGmEc3l7GALJ6KQM1D2p2bJr2Hh0H95VqRx98TutJInj3UFE0otXAib2a
1lWnP45ItndBLVCivE0SipGUDTogSHUh7iXbUplnAoGBALfGPbn5aokj2Nwco/SM
foaTOBp8AMdClPUJeWuDAwluzJIriZx2vsSWpH/A15csa//rGlcdPB90qv2rxAO7
G1DNVSxoqp5FkKkqqQigGp0JK1edcLFwZGsuvB1O3iEQ6ZOoZxAV/bC/mE1FaOfZ
vWSRmNIJ2Xhmne8sRIoQNOK6
-----END PRIVATE KEY-----
"""

creds = {
  "type": "service_account",
  "project_id": "com-webcraft-trademindai-c8f75",
  "private_key_id": "5a2ecbcb1a6f713944795093f7201dafc81c31be",
  "private_key": pk.strip(), # json.dump handles escaping newlines automatically
  "client_email": "firebase-adminsdk-fbsvc@com-webcraft-trademindai-c8f75.iam.gserviceaccount.com",
  "client_id": "104590117655426687280",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40com-webcraft-trademindai-c8f75.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

path = "backend/service-account.json"
os.makedirs("backend", exist_ok=True)
with open(path, "w") as f:
    json.dump(creds, f, indent=2)
print(f"[+] Successfully wrote verified credentials to {path}")
