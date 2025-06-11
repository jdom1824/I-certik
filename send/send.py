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

# ——————————————————————————————
# 0. Config y locale
# ——————————————————————————————
try:
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
except locale.Error:
    pass
fecha_actual = datetime.now().strftime("%d de %B de %Y")

load_dotenv()
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

if len(sys.argv) != 4:
    print("Uso: python send.py <nombre> <cedula> <correo>")
    sys.exit(1)

nombre, cedula, correo = sys.argv[1], sys.argv[2], sys.argv[3]

# ——————————————————————————————
# 1. Mint del NFT
# ——————————————————————————————
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
        raise ValueError("No vino tokenId")
    token_id = str(token_id)
    print(f"Token mintiado ID={token_id}")
except Exception as e:
    print("Error en mint:", e)
    sys.exit(1)

# ——————————————————————————————
# 2. Captura con Selenium
# ——————————————————————————————
# URL base (sin ?cedula=…), porque necesitamos interactuar.
base_url = "https://token-mamus.web.app"

# Configuramos Chrome headless
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
# Ponemos un tamaño de ventana que abarque bien el certificado
options.add_argument("--window-size=1200,900")

# Arrancamos ChromeDriver (webdriver-manager lo descarga e instala)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(base_url)

    wait = WebDriverWait(driver, 15)
    # 1) espera el input de cédula
    input_el = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, "input[type='text']"
    )))
    input_el.clear()
    input_el.send_keys(cedula)

    # 2) localiza y pulsa el botón "Buscar"
    # Ajusta esto si tu botón tiene otra clase o id
    try:
        btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    except:
        # fallback: busca el primer botón con texto “Buscar”
        for b in driver.find_elements(By.TAG_NAME, "button"):
            if b.text.strip().lower() == "buscar":
                btn = b
                break
        else:
            raise RuntimeError("No encontré el botón Buscar")

    btn.click()

    # 3) espera a que el certificado esté en pantalla
    # Debes ajustar este selector: que identifique el DIV o IMG del certificado
    certificado_sel = ".certificate-image"  # <- CAMBIA A TU SELECTOR REAL
    try:
        wait.until(EC.visibility_of_element_located((
            By.CSS_SELECTOR, certificado_sel
        )))
    except:
        # fallback: espera fija si no tienes un selector
        time.sleep(8)

    # 4) toma la captura
    os.makedirs("certificados", exist_ok=True)
    out_path = os.path.join("certificados", f"cert_{cedula}.png")
    driver.save_screenshot(out_path)
    print("Imagen generada en:", out_path)

finally:
    driver.quit()

# ——————————————————————————————
# 3. (Opcional) Envío por correo…
# ——————————————————————————————
# Aquí reactivarías tu código SMTP usando `out_path` y `token_id`.
