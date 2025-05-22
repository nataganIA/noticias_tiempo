import streamlit as st
import pandas as pd
import numpy as np
import random

# Simular datos meteorológicos (puedes reemplazar esta parte con tus propios datos)
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

# Diccionario de meses en español
meses_es = {
    1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
    5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
    9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
}

# Función de resumen
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

# Generador de noticias
def generar_noticia_con_comparativas(fecha_objetivo, df, ciudad="Madrid"):
    fecha_objetivo = pd.to_datetime(fecha_objetivo)
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

    if pd.notna(resumen['prcp_total_actual']):
        if resumen['prcp_total_actual'] == 0:
            bloque_lluvia = "No se han registrado precipitaciones"
        elif resumen['prcp_total_actual'] < 10:
            bloque_lluvia = f"Las lluvias han sido escasas, con {resumen['prcp_total_actual']:.1f} mm acumulados"
        else:
            bloque_lluvia = f"Se han recogido {resumen['prcp_total_actual']:.1f} mm de lluvia"
            if pd.notna(resumen['prcp_hist']) and resumen['prcp_hist'] > 0 and resumen['prcp_total_actual'] > 3 * resumen['prcp_hist']:
                comparativas.append(f"{mes.capitalize()} ha sido notablemente más lluvioso que la media histórica")
            elif pd.notna(resumen['prcp_hist']) and resumen['prcp_hist'] == 0 and resumen['prcp_total_actual'] > 0:
                comparativas.append("Se registraron precipitaciones donde históricamente no las había")
    else:
        bloque_lluvia = ""

    if pd.notna(resumen['tsun_total_actual']) and resumen['tsun_total_actual'] > 0:
        minutos = int(resumen['tsun_total_actual'])
        horas = minutos // 60
        resto = minutos % 60
        bloque_sol = f"El sol ha brillado durante {horas} horas y {resto} minutos"
    else:
        bloque_sol = ""

    curiosidades = []
    if pd.notna(resumen['dia_mas_calido_mes']):
        dia_calido = pd.to_datetime(resumen['dia_mas_calido_mes'])
        curiosidades.append(f"El día más cálido fue el {dia_calido.day} de {mes}")
    if pd.notna(resumen['dia_mas_frio_mes']):
        dia_frio = pd.to_datetime(resumen['dia_mas_frio_mes'])
        curiosidades.append(f"El día más frío fue el {dia_frio.day} de {mes}")

    noticia = f"{intro} {ciudad} registró {bloque_temperatura}."
    if bloque_lluvia:
        noticia += f" {bloque_lluvia}."
    if bloque_sol:
        noticia += f" {bloque_sol}."
    if comparativas:
        noticia += " " + " ".join(comparativas) + "."
    if curiosidades:
        noticia += " " + " ".join(curiosidades) + "."

    return noticia.strip()

# Interfaz Streamlit
st.title("📰 Generador automático de noticias meteorológicas")

st.markdown("Selecciona una fecha para generar la noticia basada en datos históricos y actuales.")

fecha_seleccionada = st.date_input("Fecha objetivo", pd.to_datetime("2025-04-15"))

import streamlit as st
import pandas as pd
import numpy as np
import random

# Simular datos meteorológicos (puedes reemplazar esta parte con tus propios datos)
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

# Diccionario de meses en español
meses_es = {
    1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
    5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
    9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
}

# Función de resumen
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

# Generador de noticias
def generar_noticia_con_comparativas(fecha_objetivo, df, ciudad="Madrid"):
    fecha_objetivo = pd.to_datetime(fecha_objetivo)
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

    if pd.notna(resumen['prcp_total_actual']):
        if resumen['prcp_total_actual'] == 0:
            bloque_lluvia = "No se han registrado precipitaciones"
        elif resumen['prcp_total_actual'] < 10:
            bloque_lluvia = f"Las lluvias han sido escasas, con {resumen['prcp_total_actual']:.1f} mm acumulados"
        else:
            bloque_lluvia = f"Se han recogido {resumen['prcp_total_actual']:.1f} mm de lluvia"
            if pd.notna(resumen['prcp_hist']) and resumen['prcp_hist'] > 0 and resumen['prcp_total_actual'] > 3 * resumen['prcp_hist']:
                comparativas.append(f"{mes.capitalize()} ha sido notablemente más lluvioso que la media histórica")
            elif pd.notna(resumen['prcp_hist']) and resumen['prcp_hist'] == 0 and resumen['prcp_total_actual'] > 0:
                comparativas.append("Se registraron precipitaciones donde históricamente no las había")
    else:
        bloque_lluvia = ""

    if pd.notna(resumen['tsun_total_actual']) and resumen['tsun_total_actual'] > 0:
        minutos = int(resumen['tsun_total_actual'])
        horas = minutos // 60
        resto = minutos % 60
        bloque_sol = f"El sol ha brillado durante {horas} horas y {resto} minutos"
    else:
        bloque_sol = ""

    curiosidades = []
    if pd.notna(resumen['dia_mas_calido_mes']):
        dia_calido = pd.to_datetime(resumen['dia_mas_calido_mes'])
        curiosidades.append(f"El día más cálido fue el {dia_calido.day} de {mes}")
    if pd.notna(resumen['dia_mas_frio_mes']):
        dia_frio = pd.to_datetime(resumen['dia_mas_frio_mes'])
        curiosidades.append(f"El día más frío fue el {dia_frio.day} de {mes}")

    noticia = f"{intro} {ciudad} registró {bloque_temperatura}."
    if bloque_lluvia:
        noticia += f" {bloque_lluvia}."
    if bloque_sol:
        noticia += f" {bloque_sol}."
    if comparativas:
        noticia += " " + " ".join(comparativas) + "."
    if curiosidades:
        noticia += " " + " ".join(curiosidades) + "."

    return noticia.strip()

# Interfaz Streamlit
st.title("📰 Generador automático de noticias meteorológicas")

st.markdown("Selecciona una fecha para generar la noticia basada en datos históricos y actuales.")

fecha_seleccionada = st.date_input("Fecha objetivo", pd.to_datetime("2025-04-15"))

if st.button("Generar noticia"):
    noticia = generar_noticia_con_comparativas(fecha_seleccionada, df)
    st.subheader("🗞️ Noticia generada:")
    st.write(noticia)