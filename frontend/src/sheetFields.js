export const SHEET_SECTIONS = [
  {
    id: 'overview',
    title: 'Resumen',
    fields: [
      { key: 'summary', label: 'Resumen', type: 'textarea', full: true },
      { key: 'body_type', label: 'Carrocería', type: 'text' },
      { key: 'doors', label: 'Puertas', type: 'int' },
      { key: 'seats', label: 'Plazas', type: 'int' },
      { key: 'transmission', label: 'Cambio', type: 'text' },
      { key: 'drive', label: 'Tracción', type: 'text' },
    ],
  },
  {
    id: 'dimensions',
    title: 'Dimensiones y peso',
    fields: [
      { key: 'length_mm', label: 'Largo (mm)', type: 'int' },
      { key: 'width_mm', label: 'Ancho (mm)', type: 'int' },
      { key: 'height_mm', label: 'Alto (mm)', type: 'int' },
      { key: 'wheelbase_mm', label: 'Batalla (mm)', type: 'int' },
      { key: 'weight_kg', label: 'Peso (kg)', type: 'int' },
      { key: 'fuel_tank_l', label: 'Depósito (L)', type: 'float' },
    ],
  },
  {
    id: 'performance',
    title: 'Prestaciones y consumo',
    fields: [
      { key: 'consumption_l_100km', label: 'Consumo (L/100 km)', type: 'float' },
      { key: 'co2_g_km', label: 'CO₂ (g/km)', type: 'int' },
      { key: 'acceleration_0_100', label: '0-100 (s)', type: 'float' },
      { key: 'top_speed_kmh', label: 'Vel. máx. (km/h)', type: 'int' },
    ],
  },
  {
    id: 'notes',
    title: 'Información',
    fields: [{ key: 'notes', label: 'Notas', type: 'textarea', full: true }],
  },
]

export const ENGINE_FIELDS = [
  { key: 'name', label: 'Motor', type: 'text', required: true },
  { key: 'fuel', label: 'Combustible', type: 'text' },
  { key: 'power_hp', label: 'Potencia (CV)', type: 'int' },
  { key: 'displacement_cc', label: 'Cilindrada (cc)', type: 'int' },
  { key: 'torque_nm', label: 'Par (Nm)', type: 'int' },
  { key: 'cylinders', label: 'Cilindros', type: 'int' },
  { key: 'engine_code', label: 'Código motor', type: 'text' },
]

export function emptySheetForm() {
  return Object.fromEntries(
    SHEET_SECTIONS.flatMap((s) => s.fields).map((f) => [f.key, '']),
  )
}

export function sheetToForm(sheet) {
  const form = emptySheetForm()
  if (!sheet) return form
  for (const key of Object.keys(form)) {
    const value = sheet[key]
    form[key] = value == null ? '' : String(value)
  }
  return form
}

export function engineToForm(engine) {
  return Object.fromEntries(
    ENGINE_FIELDS.map((f) => [f.key, engine?.[f.key] == null ? '' : String(engine[f.key])]),
  )
}

function parseValue(type, raw) {
  const value = String(raw ?? '').trim()
  if (value === '') return null
  if (type === 'int') {
    const n = Number.parseInt(value, 10)
    return Number.isFinite(n) ? n : null
  }
  if (type === 'float') {
    const n = Number.parseFloat(value.replace(',', '.'))
    return Number.isFinite(n) ? n : null
  }
  return value
}

export function formToSheetPayload(form) {
  const payload = {}
  for (const section of SHEET_SECTIONS) {
    for (const field of section.fields) {
      payload[field.key] = parseValue(field.type, form[field.key])
    }
  }
  return payload
}

export function formToEnginePayload(form) {
  const payload = {}
  for (const field of ENGINE_FIELDS) {
    const parsed = parseValue(field.type, form[field.key])
    if (field.required && (parsed == null || parsed === '')) {
      throw new Error('El nombre del motor es obligatorio')
    }
    payload[field.key] = parsed
  }
  return payload
}

export function formatSpec(field, value) {
  if (value == null || value === '') return null
  if (field.key === 'consumption_l_100km') return `${value} L/100 km`
  if (field.key === 'co2_g_km') return `${value} g/km`
  if (field.key === 'acceleration_0_100') return `${value} s`
  if (field.key === 'top_speed_kmh') return `${value} km/h`
  if (field.key.endsWith('_mm')) return `${value} mm`
  if (field.key === 'weight_kg') return `${value} kg`
  if (field.key === 'fuel_tank_l') return `${value} L`
  return String(value)
}

export function sheetHasContent(sheet) {
  if (!sheet) return false
  return SHEET_SECTIONS.flatMap((s) => s.fields).some((f) => {
    const v = sheet[f.key]
    return v != null && String(v).trim() !== ''
  })
}
