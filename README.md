# Motorpedia

Fichas técnicas e información de vehículos por **marca → modelo → año → motor**.

Stack: **React (Vite)** + **FastAPI** + **PostgreSQL**.

## Ramas

- `developer` — trabajo diario (local)
- `main` — lista para desplegar

## Arranque local

### 1. Base de datos

```bash
docker compose up -d
```

### 2. API (FastAPI)

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

API: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs

### 3. Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Web: http://127.0.0.1:5173

## MVP actual

- Cascada marca → modelo → año → motor y ficha técnica (dimensiones, consumo, prestaciones…).
- Crear/editar ficha y datos de motor desde la UI.
- Añadir modelo / año / motor sobre la marca seleccionada.
- Catálogo de marcas (`backend/data/brands_catalog.json`): importar nombres reales sin inventar modelos.

Seed demo: Seat / Volkswagen con unas pocas fichas de ejemplo.

## Autor

Guillermo López Argudo
