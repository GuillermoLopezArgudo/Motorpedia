import { useEffect, useState } from 'react'
import { api } from './api'

export default function WorkshopPanel({
  engineId,
  vehicle,
  sheetContent,
  editing,
  onEditSheet,
}) {
  const [categories, setCategories] = useState([])
  const [activeSlug, setActiveSlug] = useState('ficha')
  const [items, setItems] = useState([])
  const [loadingItems, setLoadingItems] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!engineId) return
    setActiveSlug('ficha')
    setItems([])
    api
      .workshop(engineId)
      .then(setCategories)
      .catch((e) => setError(e.message))
  }, [engineId])

  useEffect(() => {
    if (!engineId || !activeSlug || activeSlug === 'ficha') {
      setItems([])
      return
    }
    setLoadingItems(true)
    setError('')
    api
      .categoryItems(engineId, activeSlug)
      .then(setItems)
      .catch((e) => setError(e.message))
      .finally(() => setLoadingItems(false))
  }, [engineId, activeSlug])

  const active = categories.find((c) => c.slug === activeSlug)

  return (
    <div className="workshop">
      <nav className="category-grid" aria-label="Categorías de taller">
        {categories.map((cat) => (
          <button
            key={cat.slug}
            type="button"
            className={`category-chip ${activeSlug === cat.slug ? 'active' : ''}`}
            onClick={() => setActiveSlug(cat.slug)}
          >
            <span className="cat-name">{cat.name}</span>
            {cat.slug !== 'ficha' && (
              <span className="cat-count">{cat.item_count}</span>
            )}
          </button>
        ))}
      </nav>

      {error && <p className="error">{error}</p>}

      {activeSlug === 'ficha' ? (
        <div className="category-panel">
          <div className="sheet-head">
            <div>
              <h3>{active?.name || 'Ficha técnica'}</h3>
              {active?.description && <p className="muted">{active.description}</p>}
            </div>
            {!editing && (
              <button type="button" className="btn-secondary" onClick={onEditSheet}>
                Editar ficha
              </button>
            )}
          </div>
          {sheetContent}
        </div>
      ) : (
        <div className="category-panel">
          <h3>{active?.name || activeSlug}</h3>
          {active?.description && <p className="muted">{active.description}</p>}
          <p className="muted small">
            {vehicle.brand.name} {vehicle.model.name} {vehicle.year.year} · {vehicle.engine.name}
          </p>

          {loadingItems && <p className="muted">Cargando…</p>}

          {!loadingItems && items.length === 0 && (
            <div className="empty-state">
              <p>Aún no hay datos de «{active?.name}» para este motor.</p>
            </div>
          )}

          <ul className="item-list">
            {items.map((item) => (
              <li key={item.id} className="item-card">
                <div className="item-top">
                  <h4>{item.title}</h4>
                  {item.is_recommended && <span className="badge">Recomendado</span>}
                </div>
                <dl className="item-meta">
                  {item.oem_ref && (
                    <>
                      <dt>OEM</dt>
                      <dd>{item.oem_ref}</dd>
                    </>
                  )}
                  {item.alt_ref && (
                    <>
                      <dt>Equiv.</dt>
                      <dd>{item.alt_ref}</dd>
                    </>
                  )}
                  {item.position && (
                    <>
                      <dt>Posición</dt>
                      <dd>{item.position}</dd>
                    </>
                  )}
                  {item.quantity && (
                    <>
                      <dt>Cantidad</dt>
                      <dd>{item.quantity}</dd>
                    </>
                  )}
                  {(item.interval_km || item.interval_months) && (
                    <>
                      <dt>Intervalo</dt>
                      <dd>
                        {[
                          item.interval_km ? `${item.interval_km.toLocaleString('es-ES')} km` : null,
                          item.interval_months ? `${item.interval_months} meses` : null,
                        ]
                          .filter(Boolean)
                          .join(' / ')}
                      </dd>
                    </>
                  )}
                  {item.notes && (
                    <>
                      <dt>Notas</dt>
                      <dd>{item.notes}</dd>
                    </>
                  )}
                </dl>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
