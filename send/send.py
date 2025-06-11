import os
import sys
import requests
from dotenv import load_dotenv
from datetime import datetime
from html2image import Html2Image
import locale

# ----------------------------------------
# Configurar locale en español para fechas
# ----------------------------------------
try:
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
except locale.Error:
    # En algunos sistemas puede que no exista exactamente "es_ES.UTF-8",
    # si da error, usar la configuración por defecto o ajustar según tu SO.
    pass
fecha_actual = datetime.now().strftime("%d de %B de %Y")

# ----------------------------------------
# Cargar variables de entorno
# ----------------------------------------
load_dotenv()
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
# Si luego deseas enviar correo, necesitarás SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, etc.

# ----------------------------------------
# Validar parámetros de línea de comandos
# ----------------------------------------
if len(sys.argv) != 4:
    print("Uso: python send.py <nombre> <cedula> <correo>")
    sys.exit(1)

nombre, cedula, correo = sys.argv[1], sys.argv[2], sys.argv[3]

# ----------------------------------------
# 1. MINT del NFT
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
    response = requests.post("https://certic-44.duckdns.org/mint", json=mint_payload)
    response.raise_for_status()
    response_data = response.json()
    # Imprimir la respuesta completa para depuración
    print("Respuesta completa del mint:", response_data)
    # Extraer tokenId (ojo mayúscula en la I según tu API)
    token_id = response_data.get("tokenId")
    if token_id is None:
        print("Error: No se recibió tokenId en la respuesta.")
        sys.exit(1)
    token_id = str(token_id)
    print(f"Token mintiado: ID {token_id}")
except Exception as e:
    print(f"Error durante el mint: {e}")
    sys.exit(1)

# ----------------------------------------
# 2. GENERAR LA IMAGEN DEL CERTIFICADO
# ----------------------------------------
viewer_url = f"https://token-mamus.web.app/?cedula={cedula}"
filename = f"cert_{cedula}.png"

# Asegurar carpeta de salida
os.makedirs("certificados", exist_ok=True)

# Ruta al ejecutable de Google Chrome en tu sistema EC2
chromium_path = "/usr/bin/google-chrome"

# Instanciar Html2Image con flags para headless y virtual-time-budget
hti = Html2Image(
    output_path="certificados",
    browser_executable=chromium_path,
    custom_flags=[
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        # virtual-time-budget en milisegundos: espera hasta que pase este tiempo
        # después de completar las cargas de red, para que JS renderice el certificado.
        "--virtual-time-budget=8000"
    ]
)

try:
    # Captura la pantalla de la URL (esperando virtual-time-budget antes de disparar la captura)
    hti.screenshot(
        url=viewer_url,
        save_as=filename,
        size=(1200, 800)
    )
    ruta_imagen = os.path.join("certificados", filename)
    print(f"Imagen generada: {ruta_imagen}")
except Exception as e:
    print(f"Error al generar imagen: {e}")
    sys.exit(1)
