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

    # Atributo a analizar: EXACTITUD (rangos de valores en datos)
    add_expectation(
    "rango_edad",  # Nombre de la expectativa
    df_creditos["edad"].between(18, 100).all(),  # La validación: verifica que todos estén entre 18 y 100
    "La edad debe estar entre 18 y 100 años."  # Mensaje de error si falla
    )

    add_expectation(
    "situacion_vivienda", # Verificar que la situación de vivienda sea una de las categorías válidas
    df_creditos["situacion_vivienda"].isin(["ALQUILER", "PROPIA", "HIPOTECA", "OTROS"]).all(), # La validación a realizar
    "La situación de vivienda no se encuentra en el rango válido" 
    )

###########################################################
# TODO: Agregar al menos (2) validaciones para el dataset de tarjetas
# Por ejemplo, rangos de valores para el atributo limite de credito o el estado civil o nivel de estudios
###########################################################

# Validación 1: El límite de crédito debe ser un valor lógico (mayor o igual a 0)
    add_expectation(
        "rango_limite_credito",
        (df_tarjetas["limite_credito_tc"] >= 0).all(),
        "Error de calidad: El límite de crédito de las tarjetas no puede ser negativo."
    )

# Validación 2: El estado civil debe pertenecer a categorías conocidas
    # Nota: Ajusta los valores de la lista si en tu dataset están en minúsculas o tienen otros nombres
    add_expectation(
        "categorias_estado_civil",
        df_tarjetas["estado_civil"].isin(["CASADO", "SOLTERO", "DESCONOCIDO", "DIVORCIADO"]).all(),
        "Error de calidad: Se encontraron valores no válidos en la columna estado_civil."
    )