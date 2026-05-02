#!/bin/bash
set -e

echo "🛠️ Iniciando proceso de despliegue de Ledgera..."

# 1. Ejecutar migraciones
echo "🗄️ Ejecutando migraciones de base de datos (Alembic)..."
alembic upgrade head

# 2. Inicializar datos (usuario admin)
echo "👤 Inicializando datos de usuario..."
python app/db_init.py

# 3. Iniciar el servidor
echo "🚀 Iniciando servidor FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
