import sqlite3
import datetime
import streamlit as st
import pandas as pd # <-- Agregamos esta librería para manejar los datos del gráfico

# =====================================================================
# 1. CONFIGURACIÓN DE LA BASE DE DATOS (SQLite)
# =====================================================================
conn = sqlite3.connect("glucosa_data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS mediciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        glucosa INTEGER,
        momento TEXT,
        fecha TEXT
    )
""")
conn.commit()


# =====================================================================
# 2. INTERFAZ INTERACTIVA (Streamlit)
# =====================================================================
st.set_page_config(page_title="Monitor de Glucosa", page_icon="🩸")

st.title("🩸 Monitor de Glucosa Inteligente")
st.write("Registra tus niveles y mantén un control profesional de tu salud.")

st.subheader("📝 Nueva Medición")
nombre_usuario = st.text_input("Escribe tu nombre:", placeholder="Ej. María")
nivel_glucosa = st.number_input("Nivel de glucosa (mg/dL):", min_value=10, max_value=500, value=90)
momento_medicion = st.selectbox(
    "Momento del día:",
    ["En Ayunas", "Antes de Almorzar", "2 horas después de comer", "Antes de dormir"]
)

if st.button("Guardar Registro"):
    if nombre_usuario.strip() == "":
        st.error("⚠️ Por favor, escribe tu nombre antes de guardar.")
    else:
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        cursor.execute(
            "INSERT INTO mediciones (nombre, glucosa, momento, fecha) VALUES (?, ?, ?, ?)",
            (nombre_usuario, nivel_glucosa, momento_medicion, fecha_actual)
        )
        conn.commit()

        # =====================================================================
        # 3. LÓGICA DE ALERTAS INTELIGENTES
        # =====================================================================
        if nivel_glucosa > 120:
            st.error(f"🚨 **¡Atención {nombre_usuario}!** Tu nivel está ALTO ({nivel_glucosa} mg/dL). Te recomendamos revisar tu alimentación y consultar a tu médico.")
        elif nivel_glucosa < 70:
            st.warning(f"⚠️ **¡Alerta {nombre_usuario}!** Tu nivel está BAJO ({nivel_glucosa} mg/dL). Por favor, consume una fuente de azúcar rápido para regularizarte.")
        else:
            st.success(f"✅ **¡Excelente {nombre_usuario}!** Tu nivel está NORMAL ({nivel_glucosa} mg/dL). ¡Sigue así!")
            st.balloons()


# Leemos los datos de la base de datos para las secciones de abajo
cursor.execute("SELECT nombre, glucosa, momento, fecha FROM mediciones ORDER BY id DESC")
datos = cursor.fetchall()


# =====================================================================
# 4. GRÁFICO INTERACTIVO EN TIEMPO REAL
# =====================================================================
st.markdown("---")
st.subheader("📈 Evolución de los Niveles de Glucosa")

if datos:
    # Transformamos los datos en un formato que el gráfico entienda (DataFrame de Pandas)
    # Volteamos el orden (df[::-1]) para que el gráfico vaya del pasado al presente (de izquierda a derecha)
    df = pd.DataFrame(datos, columns=["Nombre", "Glucosa", "Momento", "Fecha"])[::-1]
    
    # Creamos el gráfico interactivo usando la Fecha como base y la Glucosa como la línea
    st.line_chart(data=df, x="Fecha", y="Glucosa")
else:
    st.info("El gráfico aparecerá automáticamente cuando ingreses datos.")


# =====================================================================
# 5. HISTORIAL EN TIEMPO REAL
# =====================================================================
st.markdown("---")
st.subheader("📊 Historial Clínico de Mediciones")

if datos:
    for fila in datos:
        nombre, glucosa, momento, fecha = fila

        if glucosa > 120:
            color = "🔴 Alto"
        elif glucosa < 70:
            color = "🟠 Bajo"
        else:
            color = "🟢 Normal"

        st.info(f"**{nombre}** | {glucosa} mg/dL ({color}) | Estado: *{momento}* | 🕒 *{fecha}*")
else:
    st.info("Aún no hay mediciones registradas. ¡Ingresa la primera!")

