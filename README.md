# AgroData Mini Pro – Analizador de datos semanales

Mini proyecto profesional en Python orientado a ciencia de datos básica aplicada al contexto rural.
Incluye un CSV sin filas repetidas, una base SQLite, visualizaciones con matplotlib, reportes y análisis por consola.

## ¿Qué incluye?
- Dataset CSV con 520 filas únicas.
- Base de datos SQLite con restricción UNIQUE (finca_id, semana).
- Script principal listo para abrir en VS Code.
- Gráficos con matplotlib.
- Exportación de reporte TXT y ranking CSV.
- Documentación técnica y esquema de base de datos.

## Estructura del proyecto
```bash
agrodata-mini-pro/
├── data/
│   ├── agrodata.db
│   └── agrodata_semanal.csv
├── docs/
│   ├── esquema_sqlite.sql
│   └── calidad_datos.md
├── reports/
├── src/
│   └── agrodata_mini_pro.py
├── README.md
└── requirements.txt
```

## Datos incluidos
La base contiene 10 fincas x 52 semanas = 520 registros únicos.

## Cómo ejecutar
1. Instala la dependencia:
```bash
python -m pip install -r requirements.txt
```

2. Ejecuta el proyecto:
```bash
python src/agrodata_mini_pro.py
```

## Funcionalidades
1. Resumen general
2. Ranking de fincas
3. Buscar una finca
4. Top de semanas
5. Generar alertas
6. Resumen por municipio
7. Validar unicidad del CSV
8. Ver gráfico de leche por finca
9. Ver gráfico semanal de una finca
10. Exportar reporte TXT
11. Exportar ranking CSV
12. Ver información de SQLite

## Garantía de unicidad
La clave lógica usada para evitar filas repetidas es:
- finca_id
- semana
- fecha_inicio

Además, SQLite refuerza esto con:
```sql
UNIQUE (finca_id, semana)

# AUTOR 
YESICA VELEZ
```
