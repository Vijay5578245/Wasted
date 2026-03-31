import os
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)
APP_URL   = os.getenv("APP_URL", "http://localhost:3000")

_SMTP_CONFIGURED = bool(SMTP_HOST and SMTP_USER and SMTP_PASS)


def _build_verification_html(username: str, verify_url: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ margin: 0; padding: 0; background: #07050f; font-family: 'Georgia', serif; }}
    .wrap {{ max-width: 480px; margin: 40px auto; padding: 48px 40px;
             background: #0d0a1a; border: 1px solid #1a1128; border-radius: 8px; }}
    h1 {{ color: #f9f7ff; font-size: 2rem; font-weight: 300;
          letter-spacing: 0.35em; margin: 0 0 8px; text-transform: uppercase; }}
    .divider {{ width: 48px; height: 1px; background: #6b1fd0; margin: 16px 0 32px; }}
    p  {{ color: #6b5d7f; font-size: 0.9rem; line-height: 1.7; margin: 0 0 24px; }}
    a.btn {{
      display: inline-block; padding: 12px 28px;
      background: transparent; border: 1px solid #6b1fd0;
      color: #c4b5fd; text-decoration: none;
      font-family: 'Inter', sans-serif; font-size: 0.7rem;
      letter-spacing: 0.2em; text-transform: uppercase; border-radius: 4px;
    }}
    .footer {{ margin-top: 40px; color: #2c2840; font-size: 0.75rem; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Wasted</h1>
    <div class="divider"></div>
    <p>Hello <strong style="color:#c4b5fd">{username}</strong>,</p>
    <p>Verify your email address to preserve your waste across sessions.</p>
    <a class="btn" href="{verify_url}">Verify Email</a>
    <p class="footer" style="margin-top:32px">
      Or copy this link:<br>
      <span style="color:#3d3757">{verify_url}</span>
    </p>
    <p class="footer">If you did not create this account, ignore this email.</p>
  </div>
</body>
</html>
"""


async def send_verification_email(to_email: str, username: str, token: str) -> None:
    if not _SMTP_CONFIGURED:
        print(f"[email] SMTP not configured — verification link: {APP_URL}/verify?token={token}")
        return

    verify_url = f"{APP_URL}/verify?token={token}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verify your Wasted account"
    msg["From"]    = SMTP_FROM
    msg["To"]      = to_email
    msg.attach(MIMEText(_build_verification_html(username, verify_url), "html"))

    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASS,
        start_tls=True,
    )
