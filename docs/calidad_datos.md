# Calidad de datos

## Resumen
- Registros totales: 520
- Fincas: 10
- Semanas: 52
- Filas duplicadas por clave lógica: 0

## Clave de control usada
Cada fila es única por la combinación:
- finca_id
- semana
- fecha_inicio

## Verificación
Durante la generación del dataset se controló que ninguna combinación repetida fuera escrita en el CSV.
Además, la base SQLite refuerza esta validación con una restricción UNIQUE (finca_id, semana).
