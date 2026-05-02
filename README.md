# Ledgera 🏦

Sistema de Tesorería para Cursos Escolares (Chile).

## Arquitectura

- **Backend:** FastAPI + PostgreSQL + Redis
- **Frontend:** Vue 3 + Vite + Tailwind CSS
- **Infraestructura:** Railway

## Estructura del Proyecto

- `backend/`: API RESTful con FastAPI.
- `frontend/`: Aplicación SPA con Vue 3.

## Desarrollo Local

### Backend
1. `cd backend`
2. `python -m venv venv`
3. `source venv/bin/activate`
4. `pip install -r requirements.txt` (Pendiente)
5. `uvicorn app.main:app --reload`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`
