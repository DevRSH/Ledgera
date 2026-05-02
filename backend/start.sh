#!/bin/sh
set -e

echo "🛠️ Iniciando Ledgera Backend..."

# 1. Migraciones (Con manejo de error si ya existen tablas)
echo "🗄️ Intentando ejecutar migraciones..."
alembic upgrade head || echo "⚠️ Las migraciones fallaron o ya estaban aplicadas. Continuando..."

# 2. Inicializar usuario
echo "👤 Verificando usuario admin..."
export PYTHONPATH=$PYTHONPATH:.
python app/db_init.py || echo "⚠️ No se pudo inicializar el usuario."


# 3. Servidor
echo "🚀 Lanzando servidor..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}


