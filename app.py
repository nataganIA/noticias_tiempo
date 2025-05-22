import streamlit as st
import pandas as pd
import numpy as np
import random

# Simular datos meteorológicos
@st.cache_data
def cargar_datos():
    fechas = pd.date_range(start="2010-01-01", end="2025-05-15", freq="D")
    np.random.seed(42)
    df = pd.DataFrame({
        'fecha': fechas,
        'temperatura_media': np.random.normal(15, 3, len(fechas)),
        'temperatura_minima': np.random.normal(8, 2, len(fechas)),
        'temperatura_maxima': np.random.normal(22, 3, len(fechas)),
        'precipitacion': np.random.exponential(2, len(fechas)),
        'duracion_sol': np.random.randint(100, 600, len(fechas)),
    })
    df['mes'] = df['fecha'].dt.month
    df['anio'] = df['fecha'].dt.year
    return df

df = cargar_datos()

meses_es = {
    1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
    5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
    9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
}

def resumen_hasta_fecha(fecha_objetivo, df):
    fecha_objetivo = pd.to_datetime(fecha_objetivo)
    df_hasta_fecha = df[df['fecha'] <= fecha_objetivo]
    mes = fecha_objetivo.month
    anio = fecha_objetivo.year

    df_mes_actual = df_hasta_fecha[(df_hasta_fecha['mes'] == mes) & (df_hasta_fecha['anio'] == anio)]
    df_historico = df_hasta_fecha[
        (df_hasta_fecha['anio'] < anio) |
        ((df_hasta_fecha['anio'] == anio) & (df_hasta_fecha['mes'] < mes))
    ]

    resumen = {
        'mes': mes,
        'anio': anio,
        'dias_con_datos_mes': len(df_mes_actual),
        'tavg_actual': df_mes_actual['temperatura_media'].mean(),
        'tmin_actual': df_mes_actual['temperatura_minima'].min(),
        'tmax_actual': df_mes_actual['temperatura_maxima'].max(),
        'prcp_total_actual': df_mes_actual['precipitacion'].sum(),
        'tsun_total_actual': df_mes_actual['duracion_sol'].sum(),
        'tavg_hist': df_historico['temperatura_media'].mean(),
        'prcp_hist': df_historico['precipitacion'].mean(),
        'max_temp_historica': df_historico['temperatura_maxima'].max(),
        'min_temp_historica': df_historico['temperatura_minima'].min(),
        'dia_mas_calido_mes': df_mes_actual.loc[df_mes_actual['temperatura_maxima'].idxmax()]['fecha']
            if not df_mes_actual.empty and not df_mes_actual['temperatura_maxima'].isnull().all() else None,
        'dia_mas_frio_mes': df_mes_actual.loc[df_mes_actual['temperatura_minima'].idxmin()]['fecha']
            if not df_mes_actual.empty and not df_mes_actual['temperatura_minima'].isnull().all() else None,
    }

    return resumen

def generar_noticia_con_comparativas(fecha_objetivo, df, ciudad="Madrid"):
    resumen = resumen_hasta_fecha(fecha_objetivo, df)
    mes = meses_es.get(resumen['mes'], 'mes desconocido')
    anio = resumen['anio']

    intro = random.choice([
        f"Hasta el {fecha_objetivo.day} de {mes} de {anio},",
        f"Durante la primera quincena de {mes} de {anio},",
        f"En lo que va de {mes} de {anio},"
    ])

    frases = []
    if pd.notna(resumen['tavg_actual']):
        frases.append(f"la temperatura media fue de {resumen['tavg_actual']:.1f}°C")
    if pd.notna(resumen['tmax_actual']):
        frases.append(f"con una máxima de {resumen['tmax_actual']:.1f}°C")
    if pd.notna(resumen['tmin_actual']):
        frases.append(f"y una mínima de {resumen['tmin_actual']:.1f}°C")
    bloque_temperatura = ", ".join(frases)

    comparativas = []
    if pd.notna(resumen['tavg_actual']) and pd.notna(resumen['tavg_hist']):
        diff = resumen['tavg_actual'] - resumen['tavg_hist']
        if abs(diff) > 0.5:
            comparativa = "más alta" if diff > 0 else "más baja"
            comparativas.append(f"Esta media fue {comparativa} que la media histórica ({resumen['tavg_hist']:.1f}°C)")

    if pd.notna(resumen['prcp_to_]()
