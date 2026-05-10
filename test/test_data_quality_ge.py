import pandas as pd
from pathlib import Path
import pytest
import warnings

warnings.filterwarnings(
    "ignore",
    message=r".*`Number` field should not be instantiated.*",
)

import great_expectations as ge

pytestmark = [
    pytest.mark.filterwarnings("ignore:.*Number.*should not be instantiated.*"),
    pytest.mark.filterwarnings("ignore:.*result_format.*Validator-level.*"),
    pytest.mark.filterwarnings("ignore:.*result_format.*Expectation-level.*"),
]

# Paths
PROJECT_DIR = Path(".").resolve()
DATA_DIR = PROJECT_DIR / "data"

def test_great_expectations():
    """ Prueba para validar la calidad de los datos utilizando Great Expectations.
    """
    # Cargar los datos de créditos y tarjetas
    df_creditos = pd.read_csv(DATA_DIR / "raw/datos_creditos.csv", sep=";")
    df_tarjetas = pd.read_csv(DATA_DIR / "raw/datos_tarjetas.csv", sep=";")

    results = {
    "success": True,
    "expectations": [],
    "statistics": {"success_count": 0, "total_count": 0}
    }

    def add_expectation(expectation_name, condition, message=""):
        results["statistics"]["total_count"] += 1
        if condition:
            results["statistics"]["success_count"] += 1
            results["expectations"].append({
                "expectation": expectation_name,
                "success": True
            })
        else:
            results["success"] = False
            results["expectations"].append({
                "expectation": expectation_name,
                "success": False,
                "message": message
            })


    # =========================================================
    # VALIDACIONES DATASET CRÉDITOS
    # =========================================================
    # Validación 1: Rango de edad (18-90 años)
    edad_valida = df_creditos["edad"].between(18, 90).all()
    mensaje_edad = ""
    if not edad_valida:
        edades_fuera = df_creditos[(df_creditos["edad"] < 18) | (df_creditos["edad"] > 90)]["edad"]
        cantidad_filas = len(edades_fuera) 
        mensaje_edad = f"Existen {cantidad_filas} filas fuera de rango. Valores exactos: {sorted(edades_fuera.unique())}"
        
    add_expectation(
        "rango_edad",
        edad_valida,
        f"La edad debe estar entre 18 y 90 años. {mensaje_edad}"
    )

    # Validación 2: Rango de valores para situacion de vivienda (ALQUILER, PROPIA, OTROS, HIPOTECA)
    vivienda_valida = df_creditos["situacion_vivienda"].isin(["ALQUILER", "PROPIA", "OTROS", "HIPOTECA"]).all()
    mensaje_vivienda = ""
    if not vivienda_valida:
        viviendas_fuera = df_creditos[~df_creditos["situacion_vivienda"].isin(["ALQUILER", "PROPIA", "OTROS", "HIPOTECA"])]["situacion_vivienda"].unique()
        mensaje_vivienda = f"Situaciones de vivienda no válidas encontradas: {sorted(viviendas_fuera)}"
    add_expectation(
        "situacion_vivienda",
        vivienda_valida,
        f"La situación de vivienda no se encuentra en el rango válido. {mensaje_vivienda}"
    )

    # =========================================================
    # VALIDACIONES DATASET TARJETAS
    # =========================================================
    # Validación 3: El límite de crédito debe ser un valor lógico (mayor o igual a 0)
    limite_valido = (df_tarjetas["limite_credito_tc"] >= 0).all()
    mensaje_limite = ""
    if not limite_valido:
        limites_fuera = df_tarjetas[df_tarjetas["limite_credito_tc"] < 0]["limite_credito_tc"].unique()
        mensaje_limite = f"Límites negativos encontrados: {sorted(limites_fuera)}"
    add_expectation(
        "rango_limite_credito",
        limite_valido,
        f"El límite de crédito de las tarjetas no puede ser negativo. {mensaje_limite}"
    )

    # Validación 4: El estado civil debe pertenecer a categorías conocidas
    categorias_civiles = ["CASADO", "SOLTERO", "DESCONOCIDO", "DIVORCIADO"]
    estado_civil_valido = df_tarjetas["estado_civil"].isin(categorias_civiles).all()
    mensaje_estado = ""
    if not estado_civil_valido:
        estados_fuera = df_tarjetas[~df_tarjetas["estado_civil"].isin(categorias_civiles)]["estado_civil"].unique()
        mensaje_estado = f"Valores no válidos encontrados: {sorted(estados_fuera)}"
    add_expectation(
        "categorias_estado_civil",
        estado_civil_valido,
        f"El estado civil debe pertenecer a las categorías esperadas. {mensaje_estado}"
    )

    # =========================================================
    # RESUMEN Y VALIDACIÓN FINAL (¡Solo uno al final!)
    # =========================================================
    print("\n" + "="*70)
    print("RESUMEN DE VALIDACIONES")
    print("="*70)
    for exp in results["expectations"]:
        status = "✓ PASS" if exp["success"] else "✗ FAIL"
        print(f"{status}: {exp['expectation']}")
        if not exp["success"] and "message" in exp:
            print(f"        Detalle: {exp['message']}")

    print(f"\nTotal: {results['statistics']['success_count']}/{results['statistics']['total_count']}")
    print("="*70 + "\n")

    # El test falla si alguna validación no pasó
    assert results["success"], f"Se encontraron {results['statistics']['total_count'] - results['statistics']['success_count']} fallos de validación."