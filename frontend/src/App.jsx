import { useEffect, useState } from 'react'
import { api } from './api'
import WorkshopPanel from './WorkshopPanel'
import {
  ENGINE_FIELDS,
  SHEET_SECTIONS,
  emptySheetForm,
  engineToForm,
  formToEnginePayload,
  formToSheetPayload,
  formatSpec,
  sheetHasContent,
  sheetToForm,
} from './sheetFields'
import './App.css'

export default function App() {
  const [brands, setBrands] = useState([])
  const [models, setModels] = useState([])
  const [years, setYears] = useState([])
  const [engines, setEngines] = useState([])
  const [catalog, setCatalog] = useState([])

  const [brandId, setBrandId] = useState('')
  const [modelId, setModelId] = useState('')
  const [yearId, setYearId] = useState('')
  const [engineId, setEngineId] = useState('')

  const [vehicle, setVehicle] = useState(null)
  const [editing, setEditing] = useState(false)
  const [sheetForm, setSheetForm] = useState(emptySheetForm())
  const [engineForm, setEngineForm] = useState(engineToForm(null))

  const [newModel, setNewModel] = useState('')
  const [newYear, setNewYear] = useState('')
  const [newEngineName, setNewEngineName] = useState('')
  const [selectedCatalog, setSelectedCatalog] = useState([])
  const [catalogFilter, setCatalogFilter] = useState('')

  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [importingTree, setImportingTree] = useState(false)
  const [treePreview, setTreePreview] = useState(null)

  const refreshBrands = () => api.brands().then(setBrands)
  const refreshCatalog = () => api.brandCatalog().then(setCatalog)

  useEffect(() => {
    Promise.all([
      refreshBrands(),
      refreshCatalog(),
      api.vehiclesCatalog().then(setTreePreview),
    ]).catch((e) => setError(e.message || 'No se pudo cargar marcas'))
  }, [])

  async function handleImportVehicleTree() {
    setImportingTree(true)
    setError('')
    setNotice('')
    try {
      const result = await api.importVehicles({})
      await refreshBrands()
      setNotice(
        `Árbol importado: +${result.brands_created} marcas, +${result.models_created} modelos, +${result.years_created} años, +${result.engines_created ?? 0} motores. ${result.note}`,
      )
    } catch (err) {
      setError(err.message)
    } finally {
      setImportingTree(false)
    }
  }

  useEffect(() => {
    setModels([])
    setYears([])
    setEngines([])
    setModelId('')
    setYearId('')
    setEngineId('')
    setVehicle(null)
    setEditing(false)
    if (!brandId) return
    api.models(brandId).then(setModels).catch((e) => setError(e.message))
  }, [brandId])

  useEffect(() => {
    setYears([])
    setEngines([])
    setYearId('')
    setEngineId('')
    setVehicle(null)
    setEditing(false)
    if (!modelId) return
    api.years(modelId).then(setYears).catch((e) => setError(e.message))
  }, [modelId])

  useEffect(() => {
    setEngines([])
    setEngineId('')
    setVehicle(null)
    setEditing(false)
    if (!yearId) return
    api.engines(yearId).then(setEngines).catch((e) => setError(e.message))
  }, [yearId])

  useEffect(() => {
    setVehicle(null)
    setEditing(false)
    if (!engineId) return
    setLoading(true)
    setError('')
    api
      .vehicle(engineId)
      .then((data) => {
        setVehicle(data)
        setSheetForm(sheetToForm(data.sheet))
        setEngineForm(engineToForm(data.engine))
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [engineId])

  const sheet = vehicle?.sheet
  const pendingCatalog = catalog.filter((b) => !b.imported)
  const filteredCatalog = pendingCatalog.filter((b) =>
    b.name.toLowerCase().includes(catalogFilter.trim().toLowerCase()),
  )

  async function handleSave(e) {
    e.preventDefault()
    if (!engineId) return
    setSaving(true)
    setError('')
    setNotice('')
    try {
      const enginePayload = formToEnginePayload(engineForm)
      const sheetPayload = formToSheetPayload(sheetForm)
      await api.updateEngine(engineId, enginePayload)
      const savedSheet = await api.saveSheet(engineId, sheetPayload)
      const refreshed = await api.vehicle(engineId)
      setVehicle(refreshed)
      setSheetForm(sheetToForm(savedSheet))
      setEngineForm(engineToForm(refreshed.engine))
      setEngines(await api.engines(yearId))
      setEditing(false)
      setNotice('Ficha guardada.')
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  async function handleCreateModel(e) {
    e.preventDefault()
    if (!brandId || !newModel.trim()) return
    try {
      const model = await api.createModel(brandId, newModel.trim())
      setModels(await api.models(brandId))
      setModelId(String(model.id))
      setNewModel('')
      setNotice(`Modelo «${model.name}» creado.`)
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleCreateYear(e) {
    e.preventDefault()
    if (!modelId || !newYear) return
    try {
      const year = await api.createYear(modelId, newYear)
      setYears(await api.years(modelId))
      setYearId(String(year.id))
      setNewYear('')
      setNotice(`Año ${year.year} creado.`)
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleCreateEngine(e) {
    e.preventDefault()
    if (!yearId || !newEngineName.trim()) return
    try {
      const engine = await api.createEngine(yearId, { name: newEngineName.trim() })
      setEngines(await api.engines(yearId))
      setEngineId(String(engine.id))
      setNewEngineName('')
      setEditing(true)
      setNotice(`Motor «${engine.name}» creado. Completa la ficha.`)
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleImportBrands() {
    if (!selectedCatalog.length) return
    setError('')
    try {
      const result = await api.importBrands(selectedCatalog)
      await Promise.all([refreshBrands(), refreshCatalog()])
      setSelectedCatalog([])
      setNotice(
        result.created.length
          ? `Importadas: ${result.created.join(', ')}.`
          : 'No había marcas nuevas que importar.',
      )
    } catch (err) {
      setError(err.message)
    }
  }

  function toggleCatalogName(name) {
    setSelectedCatalog((prev) =>
      prev.includes(name) ? prev.filter((n) => n !== name) : [...prev, name],
    )
  }

  function emptyHint() {
    if (!brandId) return 'Elige una marca para empezar la cascada marca → modelo → año → motor.'
    if (!models.length) return 'Esta marca aún no tiene modelos. Añade el primero abajo.'
    if (!modelId) return 'Selecciona un modelo.'
    if (!years.length) return 'Este modelo aún no tiene años. Añade uno.'
    if (!yearId) return 'Selecciona un año.'
    if (!engines.length) return 'Este año aún no tiene motores. Añade uno para crear su ficha.'
    if (!engineId) return 'Selecciona un motor para ver o editar la ficha técnica.'
    return null
  }

  const hint = emptyHint()

  return (
    <div className="page">
      <header className="hero">
        <p className="eyebrow">BBDD para mecánicos</p>
        <h1>Motorpedia</h1>
        <p className="lede">
          Elige marca, modelo, año y motor. Consulta ficha técnica, correas, filtros, aceites y más.
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

        {(brandId || modelId || yearId) && (
          <div className="quick-create">
            {brandId && (
              <form onSubmit={handleCreateModel} className="inline-form">
                <input
                  value={newModel}
                  onChange={(e) => setNewModel(e.target.value)}
                  placeholder="Nuevo modelo"
                  aria-label="Nuevo modelo"
                />
                <button type="submit" disabled={!newModel.trim()}>
                  Añadir modelo
                </button>
              </form>
            )}
            {modelId && (
              <form onSubmit={handleCreateYear} className="inline-form">
                <input
                  type="number"
                  min="1886"
                  max="2100"
                  value={newYear}
                  onChange={(e) => setNewYear(e.target.value)}
                  placeholder="Año"
                  aria-label="Nuevo año"
                />
                <button type="submit" disabled={!newYear}>
                  Añadir año
                </button>
              </form>
            )}
            {yearId && (
              <form onSubmit={handleCreateEngine} className="inline-form">
                <input
                  value={newEngineName}
                  onChange={(e) => setNewEngineName(e.target.value)}
                  placeholder="Nuevo motor (ej. 1.9 TDI)"
                  aria-label="Nuevo motor"
                />
                <button type="submit" disabled={!newEngineName.trim()}>
                  Añadir motor
                </button>
              </form>
            )}
          </div>
        )}

        {error && <p className="error">{error}</p>}
        {notice && <p className="notice">{notice}</p>}
        {loading && <p className="muted">Cargando ficha…</p>}

        {!loading && !vehicle && hint && (
          <div className="empty-state">
            <p>{hint}</p>
          </div>
        )}

        {vehicle && !editing && (
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
              onEditSheet={() => setEditing(true)}
              sheetContent={
                sheetHasContent(sheet) ? (
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
                              <div
                                key={field.key}
                                className={field.full ? 'spec-full' : undefined}
                              >
                                <dt>{field.label}</dt>
                                <dd>{display}</dd>
                              </div>
                            ))}
                          </dl>
                        </section>
                      )
                    })}
                  </div>
                ) : (
                  <div className="empty-state">
                    <p>Aún no hay ficha técnica para este motor.</p>
                    <button type="button" onClick={() => setEditing(true)}>
                      Crear ficha
                    </button>
                  </div>
                )
              }
            />
          </article>
        )}

        {vehicle && editing && (
          <form className="sheet-form" onSubmit={handleSave}>
            <div className="sheet-head">
              <h2>
                Editar · {vehicle.brand.name} {vehicle.model.name} {vehicle.year.year}
              </h2>
              <div className="form-actions">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => {
                    setSheetForm(sheetToForm(vehicle.sheet))
                    setEngineForm(engineToForm(vehicle.engine))
                    setEditing(false)
                  }}
                >
                  Cancelar
                </button>
                <button type="submit" disabled={saving}>
                  {saving ? 'Guardando…' : 'Guardar'}
                </button>
              </div>
            </div>

            <section className="spec-block">
              <h3>Motor</h3>
              <div className="form-grid">
                {ENGINE_FIELDS.map((field) => (
                  <label key={field.key} className={field.key === 'name' ? 'full' : undefined}>
                    {field.label}
                    <input
                      value={engineForm[field.key]}
                      onChange={(e) =>
                        setEngineForm((prev) => ({ ...prev, [field.key]: e.target.value }))
                      }
                      required={field.required}
                    />
                  </label>
                ))}
              </div>
            </section>

            {SHEET_SECTIONS.map((section) => (
              <section key={section.id} className="spec-block">
                <h3>{section.title}</h3>
                <div className="form-grid">
                  {section.fields.map((field) => (
                    <label key={field.key} className={field.full ? 'full' : undefined}>
                      {field.label}
                      {field.type === 'textarea' ? (
                        <textarea
                          rows={3}
                          value={sheetForm[field.key]}
                          onChange={(e) =>
                            setSheetForm((prev) => ({ ...prev, [field.key]: e.target.value }))
                          }
                        />
                      ) : (
                        <input
                          value={sheetForm[field.key]}
                          onChange={(e) =>
                            setSheetForm((prev) => ({ ...prev, [field.key]: e.target.value }))
                          }
                          inputMode={
                            field.type === 'int' || field.type === 'float' ? 'decimal' : undefined
                          }
                        />
                      )}
                    </label>
                  ))}
                </div>
              </section>
            ))}
          </form>
        )}
      </section>

      <section className="panel catalog">
        <div className="sheet-head">
          <div>
            <h2>Árbol de vehículos (UE)</h2>
            <p className="muted">
              Importa marca → modelo → años y motores típicos (~{treePreview?.brands ?? '…'}{' '}
              marcas). La ficha/piezas de taller se completan aparte.
            </p>
          </div>
          <button type="button" onClick={handleImportVehicleTree} disabled={importingTree}>
            {importingTree ? 'Importando…' : 'Importar / actualizar árboles y motores'}
          </button>
        </div>
      </section>

      <section className="panel catalog">
        <div className="sheet-head">
          <div>
            <h2>Catálogo de marcas</h2>
            <p className="muted">
              Lista de fabricantes reales. Importa solo nombres; los modelos se añaden después.
            </p>
          </div>
          <button
            type="button"
            onClick={handleImportBrands}
            disabled={!selectedCatalog.length}
          >
            Importar seleccionadas ({selectedCatalog.length})
          </button>
        </div>

        <label className="catalog-filter">
          Filtrar
          <input
            value={catalogFilter}
            onChange={(e) => setCatalogFilter(e.target.value)}
            placeholder="Buscar marca…"
          />
        </label>

        {pendingCatalog.length === 0 ? (
          <p className="muted">Todas las marcas del catálogo ya están en la base de datos.</p>
        ) : (
          <ul className="catalog-list">
            {filteredCatalog.map((item) => (
              <li key={item.name}>
                <label>
                  <input
                    type="checkbox"
                    checked={selectedCatalog.includes(item.name)}
                    onChange={() => toggleCatalogName(item.name)}
                  />
                  {item.name}
                </label>
              </li>
            ))}
          </ul>
        )}

        {!filteredCatalog.length && pendingCatalog.length > 0 && (
          <p className="muted">Ninguna marca coincide con el filtro.</p>
        )}
      </section>

      <footer className="foot">Motorpedia · Guillermo López Argudo</footer>
    </div>
  )
}
