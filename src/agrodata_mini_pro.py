from __future__ import annotations

import csv
import sqlite3
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "agrodata_semanal.csv"
DB_FILE = BASE_DIR / "data" / "agrodata.db"
REPORTS_DIR = BASE_DIR / "reports"


def cargar_datos() -> list[dict]:
    registros = []
    with DATA_FILE.open(encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            fila["finca_id"] = int(fila["finca_id"])
            fila["semana"] = int(fila["semana"])
            fila["litros_leche"] = int(fila["litros_leche"])
            fila["kg_maiz"] = int(fila["kg_maiz"])
            fila["kg_sorgo"] = int(fila["kg_sorgo"])
            fila["costo_alimento"] = int(fila["costo_alimento"])
            fila["lluvia_mm"] = float(fila["lluvia_mm"])
            fila["temperatura_promedio"] = float(fila["temperatura_promedio"])
            fila["animales_activos"] = int(fila["animales_activos"])
            registros.append(fila)
    return registros


def formatear_moneda(valor: float) -> str:
    return f"${valor:,.0f}".replace(",", ".")


def clasificar_produccion(promedio_leche: float) -> str:
    if promedio_leche >= 1950:
        return "Alta"
    if promedio_leche >= 1550:
        return "Media"
    return "Baja"


def resumen_general(registros: list[dict]) -> dict:
    total_leche = sum(r["litros_leche"] for r in registros)
    total_maiz = sum(r["kg_maiz"] for r in registros)
    total_sorgo = sum(r["kg_sorgo"] for r in registros)
    total_costo = sum(r["costo_alimento"] for r in registros)
    promedio_lluvia = sum(r["lluvia_mm"] for r in registros) / len(registros)
    promedio_temp = sum(r["temperatura_promedio"] for r in registros) / len(registros)
    promedio_leche = total_leche / len(registros)

    return {
        "registros": len(registros),
        "total_leche": total_leche,
        "total_maiz": total_maiz,
        "total_sorgo": total_sorgo,
        "total_costo": total_costo,
        "promedio_lluvia": promedio_lluvia,
        "promedio_temp": promedio_temp,
        "promedio_leche": promedio_leche,
        "clasificacion": clasificar_produccion(promedio_leche),
    }


def resumen_por_finca(registros: list[dict]) -> list[dict]:
    agrupado = defaultdict(lambda: {
        "finca": "",
        "municipio": "",
        "enfoque_productivo": "",
        "semanas": 0,
        "total_leche": 0,
        "total_maiz": 0,
        "total_sorgo": 0,
        "total_costo": 0,
    })

    for fila in registros:
        item = agrupado[fila["finca"]]
        item["finca"] = fila["finca"]
        item["municipio"] = fila["municipio"]
        item["enfoque_productivo"] = fila["enfoque_productivo"]
        item["semanas"] += 1
        item["total_leche"] += fila["litros_leche"]
        item["total_maiz"] += fila["kg_maiz"]
        item["total_sorgo"] += fila["kg_sorgo"]
        item["total_costo"] += fila["costo_alimento"]

    resultado = []
    for item in agrupado.values():
        item["promedio_leche"] = item["total_leche"] / item["semanas"]
        item["clasificacion"] = clasificar_produccion(item["promedio_leche"])
        resultado.append(item)

    resultado.sort(key=lambda x: x["total_leche"], reverse=True)
    return resultado


def resumen_por_municipio(registros: list[dict]) -> list[dict]:
    agrupado = defaultdict(lambda: {
        "municipio": "",
        "total_leche": 0,
        "total_costo": 0,
        "registros": 0,
    })

    for fila in registros:
        item = agrupado[fila["municipio"]]
        item["municipio"] = fila["municipio"]
        item["total_leche"] += fila["litros_leche"]
        item["total_costo"] += fila["costo_alimento"]
        item["registros"] += 1

    resultado = []
    for item in agrupado.values():
        item["promedio_leche"] = item["total_leche"] / item["registros"]
        resultado.append(item)

    resultado.sort(key=lambda x: x["total_leche"], reverse=True)
    return resultado


def top_semanas(registros: list[dict], limite: int = 10) -> list[dict]:
    return sorted(registros, key=lambda x: x["litros_leche"], reverse=True)[:limite]


def filtrar_finca(registros: list[dict], nombre_finca: str) -> list[dict]:
    nombre_finca = nombre_finca.strip().lower()
    return [fila for fila in registros if fila["finca"].lower() == nombre_finca]


def generar_alertas(registros: list[dict]) -> list[str]:
    alertas = []
    for fila in registros:
        if fila["litros_leche"] < fila["animales_activos"] * 50:
            alertas.append(
                f"Semana {fila['semana']} - {fila['finca']}: producción de leche por debajo del umbral esperado."
            )
        if fila["lluvia_mm"] > 128:
            alertas.append(
                f"Semana {fila['semana']} - {fila['finca']}: lluvia alta ({fila['lluvia_mm']} mm)."
            )
        if fila["incidencia_sanitaria"] in {"observación", "seguimiento veterinario"}:
            alertas.append(
                f"Semana {fila['semana']} - {fila['finca']}: revisar novedad sanitaria ({fila['incidencia_sanitaria']})."
            )
    return alertas


def validar_unicidad(registros: list[dict]) -> tuple[bool, int]:
    claves = {(r["finca_id"], r["semana"], r["fecha_inicio"]) for r in registros}
    return len(claves) == len(registros), len(registros) - len(claves)


def guardar_reporte_txt(registros: list[dict]) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    destino = REPORTS_DIR / "reporte_agrodata.txt"

    general = resumen_general(registros)
    fincas = resumen_por_finca(registros)[:5]
    municipios = resumen_por_municipio(registros)[:5]
    alertas = generar_alertas(registros)[:20]

    lineas = []
    lineas.append("AGRODATA MINI PRO - REPORTE EJECUTIVO")
    lineas.append("=" * 55)
    lineas.append(f"Registros analizados: {general['registros']}")
    lineas.append(f"Leche total: {general['total_leche']} litros")
    lineas.append(f"Maíz total: {general['total_maiz']} kg")
    lineas.append(f"Sorgo total: {general['total_sorgo']} kg")
    lineas.append(f"Costo total de alimento: {formatear_moneda(general['total_costo'])}")
    lineas.append(f"Promedio de lluvia: {general['promedio_lluvia']:.2f} mm")
    lineas.append(f"Promedio de temperatura: {general['promedio_temp']:.2f} °C")
    lineas.append(f"Clasificación global: {general['clasificacion']}")
    lineas.append("")
    lineas.append("TOP 5 FINCAS")
    lineas.append("-" * 55)
    for i, finca in enumerate(fincas, start=1):
        lineas.append(
            f"{i}. {finca['finca']} ({finca['municipio']}) | "
            f"Leche: {finca['total_leche']} L | Clasificación: {finca['clasificacion']}"
        )
    lineas.append("")
    lineas.append("TOP 5 MUNICIPIOS")
    lineas.append("-" * 55)
    for i, municipio in enumerate(municipios, start=1):
        lineas.append(
            f"{i}. {municipio['municipio']} | Leche: {municipio['total_leche']} L | "
            f"Costo: {formatear_moneda(municipio['total_costo'])}"
        )
    lineas.append("")
    lineas.append("ALERTAS PRINCIPALES")
    lineas.append("-" * 55)
    lineas.extend(alertas if alertas else ["Sin alertas críticas."])

    destino.write_text("\n".join(lineas), encoding="utf-8")
    return destino


def guardar_reporte_csv_ranking(registros: list[dict]) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    destino = REPORTS_DIR / "ranking_fincas.csv"
    ranking = resumen_por_finca(registros)

    with destino.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow([
            "posicion", "finca", "municipio", "enfoque_productivo",
            "total_leche", "promedio_leche", "total_maiz", "total_sorgo",
            "total_costo", "clasificacion"
        ])
        for i, finca in enumerate(ranking, start=1):
            escritor.writerow([
                i, finca["finca"], finca["municipio"], finca["enfoque_productivo"],
                finca["total_leche"], round(finca["promedio_leche"], 2),
                finca["total_maiz"], finca["total_sorgo"],
                finca["total_costo"], finca["clasificacion"]
            ])
    return destino


def mostrar_info_sqlite() -> None:
    if not DB_FILE.exists():
        print("No se encontró la base de datos SQLite.")
        return

    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        total_fincas = cur.execute("SELECT COUNT(*) FROM fincas").fetchone()[0]
        total_metricas = cur.execute("SELECT COUNT(*) FROM weekly_metrics").fetchone()[0]
        duplicados = cur.execute("""
            SELECT COUNT(*) FROM (
                SELECT finca_id, semana, COUNT(*) c
                FROM weekly_metrics
                GROUP BY finca_id, semana
                HAVING c > 1
            )
        """).fetchone()[0]

    print("\nBASE SQLITE")
    print("-" * 45)
    print(f"Fincas registradas: {total_fincas}")
    print(f"Filas en weekly_metrics: {total_metricas}")
    print(f"Duplicados por finca/semana: {duplicados}")


def graficar_leche_por_finca(registros: list[dict]) -> None:
    resumen = resumen_por_finca(registros)
    nombres = [f["finca"] for f in resumen]
    litros = [f["total_leche"] for f in resumen]

    plt.figure(figsize=(11, 6))
    plt.bar(nombres, litros)
    plt.title("Producción total de leche por finca")
    plt.xlabel("Finca")
    plt.ylabel("Litros de leche")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def graficar_tendencia_finca(registros: list[dict], nombre_finca: str) -> None:
    datos = filtrar_finca(registros, nombre_finca)
    if not datos:
        print("No se encontraron datos para esa finca.")
        return

    semanas = [fila["semana"] for fila in datos]
    litros = [fila["litros_leche"] for fila in datos]

    plt.figure(figsize=(11, 6))
    plt.plot(semanas, litros, marker="o")
    plt.title(f"Tendencia semanal de leche - {nombre_finca}")
    plt.xlabel("Semana")
    plt.ylabel("Litros de leche")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def mostrar_menu() -> None:
    print("\nAGRODATA MINI PRO - ANALIZADOR DE DATOS SEMANALES")
    print("1. Ver resumen general")
    print("2. Ver ranking de fincas")
    print("3. Buscar una finca")
    print("4. Ver top de semanas")
    print("5. Generar alertas")
    print("6. Ver resumen por municipio")
    print("7. Validar unicidad del CSV")
    print("8. Ver gráfico de leche por finca")
    print("9. Ver gráfico semanal de una finca")
    print("10. Exportar reporte TXT")
    print("11. Exportar ranking CSV")
    print("12. Ver información de SQLite")
    print("13. Salir")


def ejecutar() -> None:
    registros = cargar_datos()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            general = resumen_general(registros)
            print("\nRESUMEN GENERAL")
            print("-" * 45)
            print(f"Registros: {general['registros']}")
            print(f"Total leche: {general['total_leche']} litros")
            print(f"Total maíz: {general['total_maiz']} kg")
            print(f"Total sorgo: {general['total_sorgo']} kg")
            print(f"Costo total: {formatear_moneda(general['total_costo'])}")
            print(f"Promedio lluvia: {general['promedio_lluvia']:.2f} mm")
            print(f"Promedio temperatura: {general['promedio_temp']:.2f} °C")
            print(f"Clasificación global: {general['clasificacion']}")

        elif opcion == "2":
            print("\nRANKING DE FINCAS")
            print("-" * 90)
            for i, finca in enumerate(resumen_por_finca(registros), start=1):
                print(
                    f"{i}. {finca['finca']} | {finca['municipio']} | "
                    f"Leche: {finca['total_leche']} L | "
                    f"Promedio: {finca['promedio_leche']:.2f} | "
                    f"Clasificación: {finca['clasificacion']}"
                )

        elif opcion == "3":
            nombre = input("Ingrese el nombre exacto de la finca: ")
            datos = filtrar_finca(registros, nombre)
            if datos:
                general = resumen_general(datos)
                print(f"\nRESULTADOS PARA {nombre.upper()}")
                print("-" * 45)
                print(f"Semanas encontradas: {general['registros']}")
                print(f"Leche total: {general['total_leche']} litros")
                print(f"Maíz total: {general['total_maiz']} kg")
                print(f"Sorgo total: {general['total_sorgo']} kg")
                print(f"Costo total: {formatear_moneda(general['total_costo'])}")
                print(f"Clasificación: {general['clasificacion']}")
            else:
                print("No se encontraron datos para esa finca.")

        elif opcion == "4":
            print("\nTOP 10 SEMANAS POR PRODUCCIÓN DE LECHE")
            print("-" * 90)
            for fila in top_semanas(registros):
                print(
                    f"Semana {fila['semana']} | {fila['finca']} | "
                    f"{fila['litros_leche']} litros | {fila['fecha_inicio']}"
                )

        elif opcion == "5":
            alertas = generar_alertas(registros)
            print("\nALERTAS DETECTADAS")
            print("-" * 90)
            if alertas:
                for alerta in alertas[:30]:
                    print("-", alerta)
                if len(alertas) > 30:
                    print(f"... y {len(alertas) - 30} alertas adicionales.")
            else:
                print("No se detectaron alertas.")

        elif opcion == "6":
            print("\nRESUMEN POR MUNICIPIO")
            print("-" * 90)
            for i, municipio in enumerate(resumen_por_municipio(registros), start=1):
                print(
                    f"{i}. {municipio['municipio']} | "
                    f"Leche: {municipio['total_leche']} L | "
                    f"Promedio: {municipio['promedio_leche']:.2f} | "
                    f"Costo: {formatear_moneda(municipio['total_costo'])}"
                )

        elif opcion == "7":
            es_unico, duplicados = validar_unicidad(registros)
            print("\nVALIDACIÓN DE UNICIDAD")
            print("-" * 45)
            print(f"CSV sin duplicados: {'Sí' if es_unico else 'No'}")
            print(f"Cantidad de filas duplicadas detectadas: {duplicados}")

        elif opcion == "8":
            graficar_leche_por_finca(registros)

        elif opcion == "9":
            nombre = input("Ingrese el nombre exacto de la finca: ")
            graficar_tendencia_finca(registros, nombre)

        elif opcion == "10":
            ruta = guardar_reporte_txt(registros)
            print(f"Reporte TXT exportado en: {ruta}")

        elif opcion == "11":
            ruta = guardar_reporte_csv_ranking(registros)
            print(f"Ranking CSV exportado en: {ruta}")

        elif opcion == "12":
            mostrar_info_sqlite()

        elif opcion == "13":
            print("Gracias por usar AgroData Mini Pro.")
            break

        else:
            print("Opción inválida. Intente nuevamente.")


if __name__ == "__main__":
    ejecutar()
