import { useEffect, useState } from 'react'
import { api } from './api'
import './App.css'

export default function App() {
  const [brands, setBrands] = useState([])
  const [models, setModels] = useState([])
  const [years, setYears] = useState([])
  const [engines, setEngines] = useState([])

  const [brandId, setBrandId] = useState('')
  const [modelId, setModelId] = useState('')
  const [yearId, setYearId] = useState('')
  const [engineId, setEngineId] = useState('')

  const [vehicle, setVehicle] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api
      .brands()
      .then(setBrands)
      .catch((e) => setError(e.message || 'No se pudo cargar marcas'))
  }, [])

  useEffect(() => {
    setModels([])
    setYears([])
    setEngines([])
    setModelId('')
    setYearId('')
    setEngineId('')
    setVehicle(null)
    if (!brandId) return
    api.models(brandId).then(setModels).catch((e) => setError(e.message))
  }, [brandId])

  useEffect(() => {
    setYears([])
    setEngines([])
    setYearId('')
    setEngineId('')
    setVehicle(null)
    if (!modelId) return
    api.years(modelId).then(setYears).catch((e) => setError(e.message))
  }, [modelId])

  useEffect(() => {
    setEngines([])
    setEngineId('')
    setVehicle(null)
    if (!yearId) return
    api.engines(yearId).then(setEngines).catch((e) => setError(e.message))
  }, [yearId])

  useEffect(() => {
    setVehicle(null)
    if (!engineId) return
    setLoading(true)
    setError('')
    api
      .vehicle(engineId)
      .then(setVehicle)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [engineId])

  const sheet = vehicle?.sheet

  return (
    <div className="page">
      <header className="hero">
        <p className="eyebrow">Fichas técnicas</p>
        <h1>Motorpedia</h1>
        <p className="lede">
          Consulta información de un coche por marca, modelo, año y motor.
        </p>
      </header>

      <section className="panel">
        <div className="filters">
          <label>
            Marca
            <select value={brandId} onChange={(e) => setBrandId(e.target.value)}>
              <option value="">Selecciona marca</option>
              {brands.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Modelo
            <select
              value={modelId}
              onChange={(e) => setModelId(e.target.value)}
              disabled={!brandId}
            >
              <option value="">Selecciona modelo</option>
              {models.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Año
            <select
              value={yearId}
              onChange={(e) => setYearId(e.target.value)}
              disabled={!modelId}
            >
              <option value="">Selecciona año</option>
              {years.map((y) => (
                <option key={y.id} value={y.id}>
                  {y.year}
                </option>
              ))}
            </select>
          </label>

          <label>
            Motor
            <select
              value={engineId}
              onChange={(e) => setEngineId(e.target.value)}
              disabled={!yearId}
            >
              <option value="">Selecciona motor</option>
              {engines.map((eng) => (
                <option key={eng.id} value={eng.id}>
                  {eng.name}
                  {eng.fuel ? ` · ${eng.fuel}` : ''}
                  {eng.power_hp ? ` · ${eng.power_hp} CV` : ''}
                </option>
              ))}
            </select>
          </label>
        </div>

        {error && <p className="error">{error}</p>}
        {loading && <p className="muted">Cargando ficha…</p>}

        {vehicle && (
          <article className="sheet">
            <h2>
              {vehicle.brand.name} {vehicle.model.name} · {vehicle.year.year}
            </h2>
            <p className="engine-line">
              {vehicle.engine.name}
              {vehicle.engine.fuel ? ` · ${vehicle.engine.fuel}` : ''}
              {vehicle.engine.power_hp ? ` · ${vehicle.engine.power_hp} CV` : ''}
              {vehicle.engine.displacement_cc
                ? ` · ${vehicle.engine.displacement_cc} cc`
                : ''}
            </p>

            {sheet ? (
              <dl className="specs">
                {sheet.summary && (
                  <>
                    <dt>Resumen</dt>
                    <dd>{sheet.summary}</dd>
                  </>
                )}
                {sheet.body_type && (
                  <>
                    <dt>Carrocería</dt>
                    <dd>{sheet.body_type}</dd>
                  </>
                )}
                {sheet.doors != null && (
                  <>
                    <dt>Puertas</dt>
                    <dd>{sheet.doors}</dd>
                  </>
                )}
                {sheet.seats != null && (
                  <>
                    <dt>Plazas</dt>
                    <dd>{sheet.seats}</dd>
                  </>
                )}
                {sheet.transmission && (
                  <>
                    <dt>Cambio</dt>
                    <dd>{sheet.transmission}</dd>
                  </>
                )}
                {sheet.drive && (
                  <>
                    <dt>Tracción</dt>
                    <dd>{sheet.drive}</dd>
                  </>
                )}
                {sheet.notes && (
                  <>
                    <dt>Información</dt>
                    <dd>{sheet.notes}</dd>
                  </>
                )}
              </dl>
            ) : (
              <p className="muted">
                Aún no hay ficha técnica para este motor. Se puede crear desde la API
                (PUT /api/engines/:id/sheet).
              </p>
            )}
          </article>
        )}
      </section>

      <footer className="foot">Motorpedia · Guillermo López Argudo</footer>
    </div>
  )
}
