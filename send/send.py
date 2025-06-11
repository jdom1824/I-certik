#!/usr/bin/env python3
import os
import sys
import requests
from dotenv import load_dotenv
from datetime import datetime
import locale
import time
from string import Template

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Email imports
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.image     import MIMEImage

# ----------------------------------------
# Función para enviar el correo con plantilla
# ----------------------------------------
def send_email_with_template(to_email, nombre, fecha, ruta_cert, viewer_link, token_id, contract_address):
    # 1) Leer credenciales SMTP de .env
    SMTP_SERVER  = os.getenv("SMTP_SERVER")
    SMTP_PORT    = int(os.getenv("SMTP_PORT", 587))
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASS  = os.getenv("SENDER_PASSWORD")

    # 2) Construir URLs dinámicas
    verification_url = f"https://basescan.org/token/{contract_address}?a={token_id}"
    linkedin_share   = f"https://www.linkedin.com/sharing/share-offsite/?url={viewer_link}"

    # 3) Leer y procesar plantilla con string.Template
    tpl_path = os.path.join(os.path.dirname(__file__), "email_template.html")
    with open(tpl_path, "r", encoding="utf-8") as f:
        tpl_str = f.read()
    tpl = Template(tpl_str)
    html_body = tpl.substitute(
        nombre=nombre,
        fecha=fecha,
        linkedin_share=linkedin_share,
        verification_url=verification_url
    )

    # 4) Construir mensaje MIME
    msg = MIMEMultipart("related")
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = to_email
    msg["Subject"] = f"🎓 {nombre}, tu certificado NFT de CONEXALAB"
    msg.attach(MIMEText(html_body, "html"))

    # 5) Adjuntar la imagen del certificado
    with open(ruta_cert, "rb") as img_file:
        img = MIMEImage(img_file.read())
        img.add_header("Content-ID", "<certimg>")
        msg.attach(img)

    # 6) Enviar el correo
    with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
        print("SMTP_SERVER:", SMTP_SERVER)
        print("SMTP_PORT:", SMTP_PORT)
        print("SENDER_EMAIL:", SENDER_EMAIL)
        print("SENDER_PASS repr:", repr(SENDER_PASS))
        server.login(SENDER_EMAIL, SENDER_PASS)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

    print(f"Correo enviado exitosamente a {to_email}")

# ----------------------------------------
# 0. Configurar locale en español para fechas
# ----------------------------------------
try:
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
except locale.Error:
    pass
fecha_actual = datetime.now().strftime("%d de %B de %Y")

# ----------------------------------------
# 1. Cargar variables de entorno
# ----------------------------------------
load_dotenv()
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# ----------------------------------------
# 2. Validar argumentos
# ----------------------------------------
if len(sys.argv) != 4:
    print("Uso: python send.py <nombre> <cedula> <correo>")
    sys.exit(1)
nombre, cedula, correo = sys.argv[1], sys.argv[2], sys.argv[3]

# ----------------------------------------
# 3. MINT del NFT
# ----------------------------------------
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
    resp = requests.post("https://certic-44.duckdns.org/mint", json=mint_payload)
    resp.raise_for_status()
    data = resp.json()
    print("Respuesta mint:", data)
    token_id = data.get("tokenId")
    if token_id is None:
        raise ValueError("No se recibió tokenId")
    token_id = str(token_id)
    print(f"Token mintiado ID={token_id}")
except Exception as e:
    print("Error en mint:", e)
    sys.exit(1)

# ----------------------------------------
# 4. Captura con Selenium (solo el contenedor del certificado)
# ----------------------------------------
base_url = "https://token-mamus.web.app"
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1200,900")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(base_url)
    wait = WebDriverWait(driver, 15)

    # 4.1) Rellenar la cédula
    input_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
    input_el.clear()
    input_el.send_keys(cedula)

    # 4.2) Pulsar "Buscar"
    try:
        btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    except:
        for b in driver.find_elements(By.TAG_NAME, "button"):
            if b.text.strip().lower() == "buscar":
                btn = b
                break
        else:
            raise RuntimeError("No encontré el botón Buscar")
    btn.click()

    # 4.3) Esperar a que el contenedor del certificado sea visible
    certificado_sel = "div.certificado"  # selector del <div class="certificado">
    el_cert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, certificado_sel)))

    # 4.4) Capturar solo ese elemento
    os.makedirs("certificados", exist_ok=True)
    ruta_cert = os.path.join("certificados", f"cert_{cedula}.png")
    el_cert.screenshot(ruta_cert)
    print("Imagen del certificado guardada en:", ruta_cert)

finally:
    driver.quit()

# ----------------------------------------
# 5. Enviar el correo con la plantilla
# ----------------------------------------
viewer_link = f"https://token-mamus.web.app/?cedula={cedula}"
send_email_with_template(
    to_email         = correo,
    nombre           = nombre,
    fecha            = fecha_actual,
    ruta_cert        = ruta_cert,
    viewer_link      = viewer_link,
    token_id         = token_id,
    contract_address = CONTRACT_ADDRESS
)
