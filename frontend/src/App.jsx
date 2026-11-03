import { useEffect, useState } from 'react'
import { api } from './api'
import WorkshopPanel from './WorkshopPanel'
import {
  SHEET_SECTIONS,
  formatSpec,
  sheetHasContent,
} from './sheetFields'
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
  const [notice, setNotice] = useState('')
  const [loading, setLoading] = useState(false)
  const [booting, setBooting] = useState(true)
  const [bootMsg, setBootMsg] = useState('Preparando catálogo de vehículos…')

  useEffect(() => {
    let cancelled = false
    async function boot() {
      setBooting(true)
      setBootMsg('Cargando marcas, modelos, años y motores…')
      setError('')
      try {
        const result = await api.bootstrap()
        if (cancelled) return
        setBootMsg(result.message || 'Catálogo listo.')
        const list = await api.brands()
        if (!cancelled) {
          setBrands(list)
          setNotice(result.message)
        }
      } catch (e) {
        if (!cancelled) {
          setError(e.message || 'No se pudo preparar el catálogo')
          api.brands().then(setBrands).catch(() => {})
        }
      } finally {
        if (!cancelled) setBooting(false)
      }
    }
    boot()
    return () => {
      cancelled = true
    }
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

  function emptyHint() {
    if (booting) return 'Espera a que cargue el catálogo…'
    if (!brandId) return 'Elige una marca para empezar.'
    if (!models.length) return 'Esta marca aún no tiene modelos en el catálogo.'
    if (!modelId) return 'Selecciona un modelo.'
    if (!years.length) return 'Este modelo aún no tiene años en el catálogo.'
    if (!yearId) return 'Selecciona un año.'
    if (!engines.length) return 'Este año aún no tiene motores en el catálogo. Prueba otro año.'
    if (!engineId) return 'Selecciona un motor para ver la información.'
    return null
  }

  const hint = emptyHint()
  const filtersDisabled = booting

  const sheetContent = sheetHasContent(sheet) ? (
    <div className="sheet-sections">
      {SHEET_SECTIONS.map((section) => {
        const rows = section.fields
          .map((field) => ({
            field,
            display: formatSpec(field, sheet[field.key]),
          }))
          .filter((row) => row.display)
        if (!rows.length) return null
        return (
          <section key={section.id} className="spec-block">
            <h3>{section.title}</h3>
            <dl className="specs">
              {rows.map(({ field, display }) => (
                <div key={field.key} className={field.full ? 'spec-full' : undefined}>
                  <dt>{field.label}</dt>
                  <dd>{display}</dd>
                </div>
              ))}
            </dl>
          </section>
        )
      })}
    </div>
  ) : vehicle ? (
    <div className="sheet-sections">
      <section className="spec-block">
        <h3>Datos del motor</h3>
        <dl className="specs">
          <div>
            <dt>Motor</dt>
            <dd>{vehicle.engine.name}</dd>
          </div>
          {vehicle.engine.fuel && (
            <div>
              <dt>Combustible</dt>
              <dd>{vehicle.engine.fuel}</dd>
            </div>
          )}
          {vehicle.engine.power_hp != null && (
            <div>
              <dt>Potencia</dt>
              <dd>{vehicle.engine.power_hp} CV</dd>
            </div>
          )}
          {vehicle.engine.displacement_cc != null && (
            <div>
              <dt>Cilindrada</dt>
              <dd>{vehicle.engine.displacement_cc} cc</dd>
            </div>
          )}
          {vehicle.engine.engine_code && (
            <div>
              <dt>Código</dt>
              <dd>{vehicle.engine.engine_code}</dd>
            </div>
          )}
        </dl>
      </section>
    </div>
  ) : null

  return (
    <div className="page">
      <header className="hero">
        <p className="eyebrow">BBDD para mecánicos</p>
        <h1>Motorpedia</h1>
        <p className="lede">
          Elige marca → modelo → año → motor. Al completar la selección verás toda la ficha:
          aceites, filtros, correas, ruedas, frenos, bujías y fallos frecuentes.
        </p>
        {booting && <p className="notice">{bootMsg}</p>}
      </header>

      <section className="panel">
        <p className="muted small" style={{ marginBottom: '1rem' }}>
          {!brandId && '1/4 · Elige una marca'}
          {brandId && !modelId && '2/4 · Elige un modelo'}
          {brandId && modelId && !yearId && '3/4 · Elige un año'}
          {brandId && modelId && yearId && !engineId && '4/4 · Elige un motor'}
          {engineId && vehicle && 'Listo · Información del vehículo'}
        </p>

        <div className="filters">
          <label>
            Marca
            <select
              value={brandId}
              onChange={(e) => setBrandId(e.target.value)}
              disabled={filtersDisabled}
            >
              <option value="">{booting ? 'Cargando marcas…' : 'Selecciona marca'}</option>
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
        {notice && !booting && <p className="notice">{notice}</p>}
        {loading && <p className="muted">Cargando ficha…</p>}

        {!loading && !vehicle && hint && (
          <div className="empty-state">
            <p>{hint}</p>
          </div>
        )}

        {vehicle && (
          <article className="sheet">
            <div className="sheet-head">
              <div>
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
                  {vehicle.engine.torque_nm ? ` · ${vehicle.engine.torque_nm} Nm` : ''}
                  {vehicle.engine.engine_code ? ` · ${vehicle.engine.engine_code}` : ''}
                </p>
              </div>
            </div>

            <WorkshopPanel
              engineId={Number(engineId)}
              vehicle={vehicle}
              sheetContent={sheetContent}
            />
          </article>
        )}
      </section>

      <footer className="foot">Motorpedia · Guillermo López Argudo</footer>
    </div>
  )
}
