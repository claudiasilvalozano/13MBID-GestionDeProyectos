# Importación de librerías y supresión de advertencias
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Importación para el reporte opcional
try:
    from ydata_profiling import ProfileReport
    YDATA_DISPONIBLE = True
except ImportError:
    YDATA_DISPONIBLE = False
    print("Aviso: ydata-profiling no está instalado. Ejecuta 'pip install ydata-profiling' si deseas generar los reportes HTML.")

def visualize_data(datos_creditos: str = "data/raw/datos_creditos.csv",
                   datos_tarjetas: str = "data/raw/datos_tarjetas.csv",
                   output_dir: str = "docs/figures/") -> None:
    """
    Generar visualizaciones de los datos del escenario
    mediante gráficos de Seaborn y Matplotlib.

    Args:
        datos_creditos (str): Ruta al archivo CSV de datos de créditos.
        datos_tarjetas (str): Ruta al archivo CSV de datos de tarjetas.
        output_dir (str): Directorio donde se guardarán las figuras generadas.

    Returns:
        None
    """
    # Crear el directorio de salida si no existe
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Lectura de los datos
    df_creditos = pd.read_csv(datos_creditos, sep=";")
    df_tarjetas = pd.read_csv(datos_tarjetas, sep=";")
    sns.set_style("whitegrid")

    # Gráfico de distribución de la variable 'target'
    plt.figure(figsize=(10, 6))
    sns.countplot(x='falta_pago', data=df_creditos)
    plt.title('Distribución de la variable target')
    plt.xlabel('¿Presentó mora el cliente?')
    plt.ylabel('Cantidad de clientes')
    plt.savefig(output_dir / 'target_distribution.png')
    plt.close()

    # Gráfico de correlación entre variables numéricas - Créditos
    num_df_creditos = df_creditos.select_dtypes(include=['float64', 'int64'])
    corr_creditos = num_df_creditos.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_creditos, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Matriz de correlaciones - Créditos')
    plt.savefig(output_dir / 'correlation_heatmap_creditos.png')
    plt.close()

    # Gráfico de correlación entre variables numéricas - Tarjetas
    num_df_tarjetas = df_tarjetas.select_dtypes(include=['float64', 'int64'])
    corr_tarjetas = num_df_tarjetas.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_tarjetas, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Matriz de correlaciones - Tarjetas')
    plt.savefig(output_dir / 'correlation_heatmap_tarjetas.png')
    plt.close()

    #################################################################################################
    # TODO: Agregar al menos 2 gráficos adicionales que consideren variables relevantes 
    #################################################################################################
    
    # 1. Gráfico Adicional: Boxplot de ingresos vs falta_pago (Créditos)
    # Permite ver si los clientes con menores ingresos tienen mayor tendencia a la mora.
    if 'ingresos' in df_creditos.columns and 'falta_pago' in df_creditos.columns:
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='falta_pago', y='ingresos', data=df_creditos, palette='Set2')
        plt.title('Distribución de Ingresos según estado de Mora')
        plt.xlabel('¿Presentó mora el cliente? (0 = No, 1 = Sí)')
        plt.ylabel('Ingresos')
        plt.savefig(output_dir / 'boxplot_ingresos_mora.png')
        plt.close()

    # 2. Gráfico Adicional: Histograma de Edad según Mora (Créditos)
    # Permite analizar la distribución demográfica de los clientes que faltan a sus pagos.
    if 'edad' in df_creditos.columns and 'falta_pago' in df_creditos.columns:
        plt.figure(figsize=(10, 6))
        sns.histplot(data=df_creditos, x='edad', hue='falta_pago', kde=True, multiple='stack', palette='Set1')
        plt.title('Distribución de Edad por estado de Mora')
        plt.xlabel('Edad')
        plt.ylabel('Cantidad de Clientes')
        plt.savefig(output_dir / 'histplot_edad_mora.png')
        plt.close()

    #################################################################################################
    # OPCIÓN EXTRA: agregar la generación del reporte con ydata-profiling
    #################################################################################################
    if YDATA_DISPONIBLE:
        # Crear directorio para el reporte de verificación
        report_dir = Path("docs/reporte_verificacion")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar reporte para datos de créditos
        print("Generando reporte de profiling para datos de créditos...")
        reporte_creditos = ProfileReport(df_creditos, title="Profiling Report - Datos Créditos", explorative=True)
        reporte_creditos.to_file(report_dir / "reporte_datos_creditos.html")
        
        # Generar reporte para datos de tarjetas
        print("Generando reporte de profiling para datos de tarjetas...")
        reporte_tarjetas = ProfileReport(df_tarjetas, title="Profiling Report - Datos Tarjetas", explorative=True)
        reporte_tarjetas.to_file(report_dir / "reporte_datos_tarjetas.html")
        
        print("Reportes de ydata-profiling generados con éxito en la carpeta docs/reporte_verificacion/")


if __name__ == "__main__":
    visualize_data()