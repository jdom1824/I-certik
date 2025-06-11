import os
import sys
import requests
from dotenv import load_dotenv
from datetime import datetime
from html2image import Html2Image
import locale

# Configurar locale en español
locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
fecha_actual = datetime.now().strftime("%d de %B de %Y")

# Cargar variables de entorno
load_dotenv()
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Parámetros esperados
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
    response_data = response.json()
    print("Respuesta completa del mint:", response_data)
    token_id = str(response_data.get("tokenId"))

    if not token_id:
        print("Error: No se recibió token_id.")
        print("Respuesta completa:", response_data)
        sys.exit(1)
    print(f"Token mintiado: ID {token_id}")
except Exception as e:
    print(f"Error durante el mint: {e}")
    sys.exit(1)


# ---------- 2. HTML2IMAGE ----------
viewer_url = f"https://token-mamus.web.app/?cedula={cedula}"
filename = f"cert_{cedula}.png"

# Ruta a Google Chrome (ajustado)
chromium_path = "/usr/bin/google-chrome"  # <-- CAMBIO AQUÍ
hti = Html2Image(output_path="certificados", browser_executable=chromium_path)

try:
    os.makedirs("certificados", exist_ok=True)
    hti.screenshot(url=viewer_url, save_as=filename, size=(1200, 800))
    ruta_imagen = os.path.join("certificados", filename)
    print(f"Imagen generada: {ruta_imagen}")
except Exception as e:
    print(f"Error al generar imagen: {e}")
    sys.exit(1)

