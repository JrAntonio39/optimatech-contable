function csvCell(value) {
  const text = String(value ?? '').replaceAll('"', '""')
  return `"${text}"`
}

export function descargarCsv(nombre, columnas, filas) {
  const contenido = [columnas.map(c => csvCell(c.label)).join(';')]
  for (const fila of filas) {
    contenido.push(
      columnas
        .map(c =>
          csvCell(typeof c.value === 'function' ? c.value(fila) : fila[c.field])
        )
        .join(';')
    )
  }
  const blob = new Blob(['\ufeff' + contenido.join('\r\n')], {
    type: 'text/csv;charset=utf-8'
  })
  const url = URL.createObjectURL(blob)
  const enlace = document.createElement('a')
  enlace.href = url
  enlace.download = nombre.endsWith('.csv') ? nombre : `${nombre}.csv`
  enlace.click()
  URL.revokeObjectURL(url)
}

export function imprimirPdf() {
  window.print()
}
