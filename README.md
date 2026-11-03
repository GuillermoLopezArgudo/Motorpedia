# Motorpedia

**Autodata libre** de consulta: marca → modelo → año → motor → ficha completa (aceites, filtros, correas, ruedas, frenos, bujías, fallos).

Stack: **React (Vite)** + **FastAPI** + **PostgreSQL**.

## Ramas

- `developer` — trabajo diario
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

Al arrancar, la API importa el catálogo UE, rellena plantillas y aplica fichas **verificadas** propias.

- API: http://127.0.0.1:8000  
- Docs: http://127.0.0.1:8000/docs  
- Estado: http://127.0.0.1:8000/api/status  

### 3. Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Web: http://127.0.0.1:5173

## Qué hace (MVP consulta)

1. Elige **marca → modelo → año → motor**
2. Ves **toda** la ficha: técnica + taller
3. Etiquetas de calidad:
   - **Verificado** — curado en `backend/data/verified_workshop.json`
   - **Orientativo** — plantilla automática (no OEM de pago)

## Datos

| Archivo | Uso |
|---|---|
| `backend/data/vehicles_eu.json` | Marcas / modelos / años |
| `backend/data/engines_eu.json` | Motores conocidos |
| `backend/data/verified_workshop.json` | Fichas de taller verificadas (tú las amplías) |

Sin scrapear Autodata/TecDoc: contenido propio, legal y gratuito.

## Autor

Guillermo López Argudo
