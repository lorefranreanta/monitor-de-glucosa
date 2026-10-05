import sqlite3
import datetime
import streamlit as st

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
# 2. CONFIGURACIÓN DE PÁGINA Y ESTILOS VISUALES (HTML/CSS) - MODO OSCURO
# =====================================================================
st.set_page_config(page_title="Monitor de Glucosa", page_icon="🩸", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle, rgba(20,20,20,1) 0%, rgba(5,5,5,1) 100%);
        background-size: 400% 400%;
        animation: destellosSuaves 15s ease infinite;
    }
    
    @keyframes destellosSuaves {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    html, body, [data-testid="stWidgetLabel"], p, li, .stSelectbox, input {
        font-size: 24px !important; 
        color: #FFFFFF !important; 
        font-weight: 500 !important;
    }
    
    h1 {
        font-size: 44px !important;
        color: #FF4B4B !important; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }
    
    h2, h3 {
        font-size: 30px !important;
        color: #E0E0E0 !important;
    }

    input {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #111111 !important; 
        font-size: 22px !important;
    }
    
    .stAlert p {
        color: #111111 !important; 
        font-size: 22px !important;
    }
    </style>
    """, unsafe_allow_html=True)


# =====================================================================
# 3. INTERFAZ INTERACTIVA ACCESIBLE (Streamlit)
# =====================================================================
st.title("🩸 Monitor de Glucosa")
st.write("Guarde sus niveles de forma fácil y segura. Diseñado para una lectura clara.")

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
            st.warning(f"⚠️ **¡Alerta {nombre_usuario}!** Tu nivel está BAJO ({nivel_glucosa} mg/dL). Por favor, consume una fuente de azúcar rápido.")
        else:
            st.success(f"✅ **¡Excelente {nombre_usuario}!** Tu nivel está NORMAL ({nivel_glucosa} mg/dL). ¡Sigue así!")
            st.balloons()


# Leemos los datos guardados de la base de datos
cursor.execute("SELECT nombre, glucosa, momento, fecha FROM mediciones ORDER BY id DESC")
datos = cursor.fetchall()


# =====================================================================
# 5. HISTORIAL CLÍNICO DE SEGUIMIENTO
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

        st.info(f"**{nombre}** | **{glucosa} mg/dL** ({color}) | Estado: *{momento}* | 🕒 *{fecha}*")
else:
    st.info("Aún no hay mediciones registradas. ¡Ingresa la primera para iniciar el historial!")


# =====================================================================
# 6. BOTÓN DE SEGURIDAD PARA REINICIAR DATOS (Reset)
# =====================================================================
if datos:
    st.markdown("---")
    st.subheader("⚙️ Zona de Peligro")
    
    # Primero el usuario presiona el botón principal de intentar borrar
    if st.button("🗑️ Borrar todo el Historial"):
        st.session_state.confirmar_borrado = True

    # Si lo presionó, se despliega esta segunda advertencia de confirmación por seguridad
    if st.get_value_checkbox if hasattr(st, 'get_value_checkbox') else st.session_state.get('confirmar_borrado', False):
        st.warning("⚠️ ¿Está completamente seguro? Esta acción eliminará permanentemente todos los registros y no se puede deshacer.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("❌ Cancelar"):
                st.session_state.confirmar_borrado = False
                st.rerun()
        with col2:
            if st.button("💥 Sí, borrar de todos modos"):
                # Ejecutamos la orden SQL para vaciar la tabla
                cursor.execute("DELETE FROM mediciones")
                conn.commit()
                st.session_state.confirmar_borrado = False
                st.success("¡Historial médico eliminado con éxito!")
                st.rerun() # Recarga la pantalla para mostrar el historial vacío
