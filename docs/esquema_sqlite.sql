CREATE TABLE fincas (
    finca_id INTEGER PRIMARY KEY,
    finca TEXT NOT NULL,
    municipio TEXT NOT NULL,
    enfoque_productivo TEXT NOT NULL
);

CREATE TABLE weekly_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    finca_id INTEGER NOT NULL,
    semana INTEGER NOT NULL,
    fecha_inicio TEXT NOT NULL,
    litros_leche INTEGER NOT NULL,
    kg_maiz INTEGER NOT NULL,
    kg_sorgo INTEGER NOT NULL,
    costo_alimento INTEGER NOT NULL,
    lluvia_mm REAL NOT NULL,
    temperatura_promedio REAL NOT NULL,
    animales_activos INTEGER NOT NULL,
    incidencia_sanitaria TEXT NOT NULL,
    observacion TEXT NOT NULL,
    FOREIGN KEY (finca_id) REFERENCES fincas(finca_id),
    UNIQUE (finca_id, semana)
);
