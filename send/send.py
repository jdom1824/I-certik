#!/usr/bin/env python3
import os
import sys
import requests
from dotenv import load_dotenv
from datetime import datetime
import locale
import time

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

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
# Si luego vas a enviar correo necesitarás también SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD en tu .env

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
    token_id = data.get("tokenId")  # ojo: la API devuelve "tokenId"
    if token_id is None:
        raise ValueError("No se recibió tokenId en la respuesta")
    token_id = str(token_id)
    print(f"Token mintiado ID={token_id}")
except Exception as e:
    print("Error en mint:", e)
    sys.exit(1)

# ----------------------------------------
# 4. Generar captura con Selenium (solo la <img>)
# ----------------------------------------
base_url = "https://token-mamus.web.app"

# Configuración de Chrome en modo headless
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

    # 4.1) Rellenar cédula
    input_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
    input_el.clear()
    input_el.send_keys(cedula)

    # 4.2) Pulsar "Buscar"
    try:
        btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    except:
        # Fallback: buscar por texto
        for b in driver.find_elements(By.TAG_NAME, "button"):
            if b.text.strip().lower() == "buscar":
                btn = b
                break
        else:
            raise RuntimeError("No encontré el botón Buscar")
    btn.click()

    # 4.3) Esperar a que el <img> del certificado sea visible
    certificado_sel = "img.certificate-image"  # <-- AJUSTA este selector a tu HTML real
    el_cert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, certificado_sel)))

    # 4.4) Tomar screenshot solo del elemento <img>
    os.makedirs("certificados", exist_ok=True)
    ruta_cert = os.path.join("certificados", f"cert_{cedula}.png")
    el_cert.screenshot(ruta_cert)
    print("Imagen del certificado guardada en:", ruta_cert)

finally:
    driver.quit()

# ----------------------------------------
# 5. (Opcional) Envío de correo
# ----------------------------------------
# Si ya lo tienes preparado, aquí podrías reactivar tu código de smtplib
# usando `ruta_cert` y `token_id`. Guárdate este valor para adjuntar.
