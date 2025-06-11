#!/bin/bash

# Ruta al CSV (ajusta si es necesario)
CSV="studenst.csv"

# Saltar encabezado y leer línea por línea
tail -n +2 "$CSV" | while IFS=',' read -r name id email _; do
  # Quitar comillas si existen
  name=$(echo "$name" | tr -d '"')
  email=$(echo "$email" | tr -d '"')
  id=$(echo "$id" | tr -d '"')

  # Ejecutar el comando
  echo "Procesando: $name - $id - $email"
  python send.py "$name" "$id" "$email"
done
