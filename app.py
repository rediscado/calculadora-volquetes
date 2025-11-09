
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Calculadora de Transporte de Rocas", layout="centered")

st.title("🔧 Calculadora de Transporte de Rocas")
st.write("App demo: calcula tiempos y sugiere la mejor combinación de equipo y ruta según la cantidad de volquetes.")

# --- Sidebar: parámetros editables ---
st.sidebar.header("Parámetros (editable)")
st.sidebar.markdown("Ajusta los tiempos de carga y transporte según lo necesites.")

# Default times (minutes)
default_tiempo_carga = {
    "Cargador frontal": 8.0,
    "Excavadora": 12.0,
    "Mixto": 10.0
}
default_tiempo_transporte = {
    "Ruta 1": 15.0,
    "Ruta 2": 18.0,
    "Ruta 3": 12.0,
    "Ruta 4": 25.0,
    "Ruta 5": 20.0
}

# Allow user to edit defaults
tiempo_carga = {}
tiempo_transporte = {}

st.sidebar.subheader("Tiempo de carga (min por volquete)")
for k, v in default_tiempo_carga.items():
    tiempo_carga[k] = st.sidebar.number_input(f"{k}", value=float(v), min_value=0.0, step=0.5)

st.sidebar.subheader("Tiempo de transporte (min por viaje)")
for k, v in default_tiempo_transporte.items():
    tiempo_transporte[k] = st.sidebar.number_input(f"{k}", value=float(v), min_value=0.0, step=0.5)

st.sidebar.markdown("---")
st.sidebar.write("Modelo simple: Tiempo total = (tiempo_carga + tiempo_transporte) * número_de_viajes")
st.sidebar.write("Número de viajes = cantidad_de_volquetes (asume 1 volquete = 1 viaje)")

# --- Main inputs ---
st.subheader("Entradas")
volquetes = st.number_input("Cantidad de volquetes (número de viajes)", min_value=1, value=5, step=1)
equipo = st.selectbox("Equipo de carguío (selecciona para ver resultados)", list(tiempo_carga.keys()))
ruta = st.selectbox("Ruta (selecciona para ver resultados)", list(tiempo_transporte.keys()))

# Compute selected combination result
tiempo_seleccion = (tiempo_carga[equipo] + tiempo_transporte[ruta]) * volquetes
st.metric("⏱️ Tiempo estimado (selección actual)", f"{tiempo_seleccion:.1f} minutos")

# --- Solver: evalúa todas las combinaciones y sugiere la mejor ---
st.subheader("Solver: comparar todas las combinaciones")
rows = []
for eq_k, eq_v in tiempo_carga.items():
    for rt_k, rt_v in tiempo_transporte.items():
        tiempo_total = (eq_v + rt_v) * volquetes
        rows.append({
            "Equipo": eq_k,
            "Ruta": rt_k,
            "Tiempo por viaje (min)": eq_v + rt_v,
            "Tiempo total (min)": tiempo_total
        })

df = pd.DataFrame(rows)
df_sorted = df.sort_values("Tiempo total (min)").reset_index(drop=True)

st.write("Tabla de combinaciones ordenada por tiempo total (menor primero):")
st.dataframe(df_sorted)

best = df_sorted.iloc[0]
st.success(f"Mejor alternativa: **{best['Equipo']}** + **{best['Ruta']}** → {best['Tiempo total (min)']:.1f} minutos")

# --- Visualización simple ---
st.subheader("Comparación gráfica")
# Simple bar plot using Streamlit built-in chart (no colors forced)
chart_data = df_sorted[["Equipo", "Ruta", "Tiempo total (min)"]].copy()
chart_data["combinacion"] = chart_data["Equipo"] + " • " + chart_data["Ruta"]
chart_data = chart_data.set_index("combinacion")
st.bar_chart(chart_data["Tiempo total (min)"])

# --- Exportar resultados ---
st.subheader("Exportar")
with st.expander("Opciones de exportación"):
    if st.button("Descargar tabla CSV"):
        csv = df_sorted.to_csv(index=False).encode('utf-8')
        st.download_button("Descargar CSV", data=csv, file_name="combos_tiempo.csv", mime="text/csv")
    if st.button("Descargar resumen de la mejor opción (TXT)"):
        resumen = f"Mejor alternativa: {best['Equipo']} + {best['Ruta']} -> {best['Tiempo total (min)']:.1f} minutos"
        st.download_button("Descargar TXT", data=resumen, file_name="mejor_alternativa.txt", mime="text/plain")

st.markdown("---")
st.caption("Este es un prototipo. Podemos añadir más variables: capacidad por volquete, tiempos de desplazamiento por congestión, ciclos de carga/descarga, o un optimizador que busque minimizar costo en vez de tiempo.")
