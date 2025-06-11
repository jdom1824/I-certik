import os
import sys
import requests
import smtplib
from dotenv import load_dotenv
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from html2image import Html2Image
import locale

# Locale español para la fecha
locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
fecha_actual = datetime.now().strftime("%d de %B de %Y")

# Cargar variables .env
load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Parámetros desde la línea de comandos
if len(sys.argv) != 4:
    print("Uso: python send.py <nombre> <cedula> <correo>")
    sys.exit(1)

nombre, cedula, correo = sys.argv[1], sys.argv[2], sys.argv[3]

# ---------- 1. MINT ----------
descripcion = (
    "This certificate recognizes your participation in the 2024 Aerospace Engineering Bootcamp, "
    "held at Colegio Interamericano from April 8 to 13, 2024. We proudly acknowledge your dedication "
    "to learning and applying rocket engineering for a total of 25 hours."
)
fecha_api = "04/11/2024"

mint_payload = {
    "nombre": nombre,
    "cedula": cedula,
    "descripcion": descripcion,
    "fecha": fecha_api
}

try:
    response = requests.post("https://certic-44.duckdns.org/mint", json=mint_payload)
    response.raise_for_status()
    token_id = str(response.json().get("token_id"))
    if not token_id:
        print("❌ No se recibió token_id.")
        sys.exit(1)
    print(f"✅ Token mintiado: ID {token_id}")
except Exception as e:
    print(f"❌ Error mint: {e}")
    sys.exit(1)

# ---------- 2. HTML2IMAGE ----------
viewer_url = f"https://token-mamus.web.app/?cedula={cedula}"
hti = Html2Image(output_path="certificados")
filename = f"cert_{cedula}.png"

try:
    hti.screenshot(url=viewer_url, save_as=filename, size=(1200, 800), wait_time=2)
    ruta_imagen = os.path.join("certificados", filename)
    print(f"📷 Imagen generada: {ruta_imagen}")
except Exception as e:
    print(f"❌ Error al generar imagen: {e}")
    sys.exit(1)

# ---------- 3. ENVÍO DE CORREO ----------
msg = MIMEMultipart()
msg["From"] = SENDER_EMAIL
msg["To"] = correo
msg["Subject"] = "🎓 Tu certificado NFT ha sido emitido"

verification_link = f"https://basescan.org/token/{CONTRACT_ADDRESS}?a={token_id}"
survey_link = "https://forms.gle/JYKhskqraj9RnYuy9"
viewer_link = viewer_url

html = f"""
<html>
  <body style="font-family: Arial; text-align: center; background: #f4f4f4; padding: 20px;">
    <div style="background: #fff; padding: 30px; border-radius: 10px;">
      <h1>¡Felicidades, {nombre}!</h1>
      <p>Tu certificado NFT ha sido generado exitosamente.</p>
      <p><strong>Fecha de emisión:</strong> {fecha_actual}</p>
      <img src="cid:certimg" alt="Certificado" style="width: 100%; max-width: 600px; border-radius: 10px;" />
      <p>
        <a href="{viewer_link}" style="background:#00C6B4;color:#fff;padding:10px 20px;border-radius:5px;text-decoration:none;margin:10px;">Ver Certificado</a>
        <a href="{verification_link}" style="background:#003A54;color:#fff;padding:10px 20px;border-radius:5px;text-decoration:none;margin:10px;">Ver en Blockchain</a>
        <a href="{survey_link}" style="background:#888;color:#fff;padding:10px 20px;border-radius:5px;text-decoration:none;margin:10px;">Encuesta</a>
      </p>
      <p style="font-size: 12px; color: #888;">Emitido por ConexaLab – Blockchain para Industria 5.0</p>
    </div>
  </body>
</html>
"""

msg.attach(MIMEText(html, "html"))

# Adjuntar imagen
try:
    with open(ruta_imagen, "rb") as f:
        img = MIMEImage(f.read())
        img.add_header("Content-ID", "<certimg>")
        msg.attach(img)
except Exception as e:
    print(f"❌ Error adjuntando imagen: {e}")
    sys.exit(1)

# Enviar el correo
try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, correo, msg.as_string())
    print(f"📨 Correo enviado exitosamente a {correo}")
except Exception as e:
    print(f"❌ Error enviando correo: {e}")
