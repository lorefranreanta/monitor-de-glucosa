import sqlite3
import datetime
import streamlit as st
import pandas as pd

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
# 2. CONFIGURACIÓN DE PÁGINA Y ESTILOS VISUALES (HTML/CSS)
# =====================================================================
st.set_page_config(page_title="Monitor de Glucosa", page_icon="🩸", layout="centered")

# Código CSS para fondo animado rojo con destellos blancos y letras grandes
st.markdown("""
    <style>
    /* 1. Fondo rojo con animación de destellos blancos */
    .stApp {
        background: radial-gradient(circle, rgba(215,35,35,1) 0%, rgba(135,15,15,1) 100%);
        background-size: 400% 400%;
        animation: destellos 10s ease infinite;
    }
    
    @keyframes destellos {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; rgba(255,255,255,0.15) 0% }
        100% { background-position: 0% 50%; }
    }

    /* 2. Accesibilidad: Aumentar tamaño de letras para mayores de 55 años */
    html, body, [data-testid="stWidgetLabel"], p, li, .stSelectbox, input {
        font-size: 24px !important; /* Letras normales y etiquetas mucho más grandes */
        color: #FFFFFF !important; /* Texto blanco para resaltar sobre el fondo rojo */
        font-weight: 500 !important;
    }
    
    /* Títulos principales gigantes */
    h1 {
        font-size: 48px !important;
        color: #FFFFFF !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    /* Subtítulos grandes */
    h2, h3 {
        font-size: 32px !important;
        color: #FFF0F0 !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }

    /* Estilo especial para los textos dentro de las cajas de entrada */
    input {
        background-color: rgba(255, 255, 255, 0.9) !important;
        color: #333333 !important; /* Texto oscuro dentro del input para que se lea bien */
        font-size: 22px !important;
    }
    
    /* Ajuste para que los textos de las alertas sigan siendo legibles */
    .stAlert p {
        color: #333333 !important; /* Texto oscuro dentro de las alertas para contraste */
        font-size: 22px !important;
    }
    </style>
    """, unsafe_allow_html=True)


# =====================================================================
# 3. INTERFAZ INTERACTIVA CON TEXTO GRANDE (Streamlit)
# =====================================================================
st.title("🩸 Monitor de Glucosa Inteligente")
st.write("Guarde sus niveles de forma fácil. Diseñado para una lectura clara.")

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
        # 4. LÓGICA DE ALERTAS INTELIGENTES
        # =====================================================================
        if nivel_glucosa > 120:
            st.error(f"🚨 **¡Atención {nombre_usuario}!** Tu nivel está ALTO ({nivel_glucosa} mg/dL). Te recomendamos revisar tu alimentación y consultar a tu médico.")
        elif nivel_glucosa < 70:
            st.warning(f"⚠️ **¡Alerta {nombre_usuario}!** Tu nivel está BAJO ({nivel_glucosa} mg/dL). Por favor, consume una fuente de azúcar rápido para regularizarte.")
        else:
            st.success(f"✅ **¡Excelente {nombre_usuario}!** Tu nivel está NORMAL ({nivel_glucosa} mg/dL). ¡Sigue así!")
            st.balloons()


# Leemos los datos de la base de datos
cursor.execute("SELECT nombre, glucosa, momento, fecha FROM mediciones ORDER BY id DESC")
datos = cursor.fetchall()


# =====================================================================
# 5. GRÁFICO INTERACTIVO EN TIEMPO REAL
# =====================================================================
st.markdown("---")
st.subheader("📈 Evolución de los Niveles de Glucosa")

if datos:
    df = pd.DataFrame(datos, columns=["Nombre", "Glucosa", "Momento", "Fecha"])[::-1]
    st.line_chart(data=df, x="Fecha", y="Glucosa")
else:
    st.info("El gráfico aparecerá automáticamente cuando ingreses datos.")


# =====================================================================
# 6. HISTORIAL EN TIEMPO REAL
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
