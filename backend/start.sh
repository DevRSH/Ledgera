#!/bin/sh
set -e

echo "🛠️ Iniciando Ledgera Backend..."

# 1. Migraciones
echo "🗄️ Migraciones..."
alembic upgrade head

# 2. Inicializar usuario
echo "👤 Inicializando usuario admin..."
python app/db_init.py

# 3. Servidor
echo "🚀 Servidor FastAPI en puerto ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

