import { useEffect, useState } from 'react'
import { api } from './api'

function ItemCard({ item }) {
  return (
    <li className="item-card">
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
  )
}

export default function WorkshopPanel({
  engineId,
  vehicle,
  sheetContent,
  editing,
  onEditSheet,
}) {
  const [sections, setSections] = useState([])
  const [activeSlug, setActiveSlug] = useState('todo')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!engineId) return
    setActiveSlug('todo')
    setLoading(true)
    setError('')
    api
      .workshopFull(engineId)
      .then(setSections)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [engineId])

  const chips = [
    { slug: 'todo', name: 'Todo', item_count: sections.reduce((n, s) => n + s.item_count, 0) },
    { slug: 'ficha', name: 'Ficha técnica', item_count: null },
    ...sections.map((s) => ({
      slug: s.slug,
      name: s.name,
      item_count: s.item_count,
    })),
  ]

  const visibleSections =
    activeSlug === 'todo'
      ? sections
      : sections.filter((s) => s.slug === activeSlug)

  return (
    <div className="workshop">
      <nav className="category-grid" aria-label="Categorías de taller">
        {chips.map((cat) => (
          <button
            key={cat.slug}
            type="button"
            className={`category-chip ${activeSlug === cat.slug ? 'active' : ''}`}
            onClick={() => setActiveSlug(cat.slug)}
          >
            <span className="cat-name">{cat.name}</span>
            {cat.item_count != null && <span className="cat-count">{cat.item_count}</span>}
          </button>
        ))}
      </nav>

      {error && <p className="error">{error}</p>}
      {loading && <p className="muted">Cargando ficha completa del vehículo…</p>}

      {activeSlug === 'ficha' ? (
        <div className="category-panel">
          <div className="sheet-head">
            <div>
              <h3>Ficha técnica</h3>
              <p className="muted">Datos generales del vehículo</p>
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
          <p className="muted small">
            {vehicle.brand.name} {vehicle.model.name} {vehicle.year.year} ·{' '}
            {vehicle.engine.name}
          </p>

          {!loading && visibleSections.length === 0 && (
            <div className="empty-state">
              <p>Sin datos de taller para este motor todavía.</p>
            </div>
          )}

          {visibleSections.map((section) => (
            <section key={section.slug} className="spec-block workshop-section">
              <h3>
                {section.name}
                <span className="cat-count inline">{section.item_count}</span>
              </h3>
              {section.description && <p className="muted small">{section.description}</p>}
              {section.items.length === 0 ? (
                <p className="muted">Sin ítems en esta categoría.</p>
              ) : (
                <ul className="item-list">
                  {section.items.map((item) => (
                    <ItemCard key={item.id} item={item} />
                  ))}
                </ul>
              )}
            </section>
          ))}
        </div>
      )}
    </div>
  )
}
