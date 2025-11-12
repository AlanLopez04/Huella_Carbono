import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from mapa_interactivo import crear_mapa_con_filtros, crear_panel_filtros, crear_tabla_municipios_filtrados

# ===== IMPORTS PARA SISTEMA DE REGLAS =====
from motor_inferencia import MotorInferencia, Hecho
from firebase_config import FirebaseConnection

# Inicializar motor de inferencia (se cachea para eficiencia)
@st.cache_resource
def inicializar_motor():
    """
    Inicializa el motor de inferencia una sola vez por sesión.
    
    REGLA DE NEGOCIO: El motor se carga al inicio para
    optimizar el rendimiento de la aplicación.
    """
    return MotorInferencia()

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Huella de Carbono - Hidalgo",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #4CAF50 0%, #81C784 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
    }
    .perfil-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .municipio-info {
        background-color: #E8F5E9;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Cargar datos
@st.cache_data
def cargar_datos():
    """Carga el dataset de huella de carbono"""
    try:
        df = pd.read_csv('huella_carbono_hidalgo_realista.csv')
        return df
    except FileNotFoundError:
        st.error("⚠️ No se encontró el archivo 'huella_carbono_hidalgo_realista.csv'. Por favor genera el dataset primero.")
        st.stop()

# Definición de perfiles
# Definición de perfiles
PERFILES = {
    "El principiante": {
        "descripcion": "Interesado en el tema, pero no sabe por dónde empezar.",
        "motivacion": "Quiere entender su impacto de forma sencilla",
        "descripcion_ampliada": """
            El perfil de **principiante** corresponde a personas que están dando sus primeros pasos 
            en el cuidado del medio ambiente. Son individuos conscientes de la crisis climática pero 
            que aún no han profundizado en el tema. Buscan información accesible, visual y fácil de 
            entender sin sentirse abrumados por datos técnicos. Valoran las sugerencias prácticas 
            que puedan implementar de inmediato en su vida diaria, como pequeños cambios en sus 
            hábitos de consumo y transporte. Este perfil representa a la mayoría de la población que 
            desea contribuir positivamente pero necesita orientación clara sobre cómo empezar.
        """,
        "icono": "🌱",
        "color": "#4CAF50"
    },
    "El ecologista comprometido": {
        "descripcion": "Busca información detallada y precisa para optimizar sus esfuerzos.",
        "motivacion": "Optimizar y reducir al máximo su huella",
        "descripcion_ampliada": """
            El perfil de **ecologista comprometido** corresponde a personas profundamente 
            involucradas en la causa ambiental. Son individuos que han educado sobre 
            sostenibilidad y buscan maximizar su impacto positivo. Requieren datos precisos, 
            métricas detalladas y análisis profundos para tomar decisiones informadas. Están 
            dispuestos a hacer cambios significativos en su estilo de vida, incluyendo 
            inversiones económicas en tecnologías limpias como paneles solares o vehículos 
            eléctricos. Valoran el rigor científico, participan activamente en iniciativas 
            comunitarias y buscan constantemente nuevas formas de reducir su huella de carbono. 
            Este perfil representa a los líderes del cambio ambiental en sus comunidades.
        """,
        "icono": "♻️",
        "color": "#2E7D32"
    },
    "La familia consciente": {
        "descripcion": "Quiere entender y reducir la huella de toda la familia.",
        "motivacion": "Reducir el impacto familiar y enseñar hábitos sostenibles",
        "descripcion_ampliada": """
            El perfil de **familia consciente** corresponde a núcleos familiares que desean 
            adoptar prácticas sostenibles como grupo. Son familias que reconocen la importancia 
            de educar a sus hijos en valores ambientales y buscan crear hábitos colectivos que 
            beneficien al planeta. Priorizan actividades que puedan realizar juntos, como reciclar, 
            compostar, o usar transporte compartido. Buscan equilibrar la sostenibilidad con las 
            necesidades prácticas de la vida familiar: presupuesto, tiempo y comodidad. Valoran 
            las soluciones que puedan involucrar a todos los miembros, desde los más pequeños 
            hasta los adultos mayores. Este perfil representa a familias que quieren dejar un 
            mejor planeta para las futuras generaciones y entienden que el cambio comienza en casa.
        """,
        "icono": "👨‍👩‍👧‍👦",
        "color": "#1976D2"
    }
}

def mostrar_info_municipio(datos_municipio):
    """Muestra información detallada del municipio seleccionado"""
    
    st.markdown(f"""
        <div class="municipio-info">
            <h2>📍 {datos_municipio['municipio']}</h2>
            <p><strong>Tipo:</strong> {datos_municipio['tipo_municipio']}</p>
            <p><strong>Característica especial:</strong> {datos_municipio['caracteristica_especial']}</p>
            <p><strong>Población:</strong> {datos_municipio['poblacion']:,} habitantes</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🏭 Emisión Total",
            f"{datos_municipio['emision_total_ton']:,.0f} ton",
            delta=None
        )
    
    with col2:
        st.metric(
            "👤 Per Cápita",
            f"{datos_municipio['emision_per_capita_kg']:,.0f} kg",
            delta=None
        )
    
    with col3:
        nivel_color = {
            "Muy Alto": "🔴",
            "Alto": "🟠",
            "Medio": "🟡",
            "Bajo": "🟢",
            "Muy Bajo": "🔵"
        }
        st.metric(
            "📊 Nivel",
            f"{nivel_color.get(datos_municipio['nivel_contaminacion'], '⚪')} {datos_municipio['nivel_contaminacion']}",
            delta=None
        )
    
    with col4:
        st.metric(
            "💰 Ingreso Promedio",
            f"${datos_municipio['nivel_ingreso_promedio_mxn']:,.0f}",
            delta=None
        )
    
    # Gráfico de emisiones por categoría
    st.subheader("📊 Emisiones por Categoría")
    
    categorias = ['Transporte', 'Energía', 'Residuos', 'Industria', 'Agricultura']
    valores = [
        datos_municipio['emision_transporte_ton'],
        datos_municipio['emision_energia_ton'],
        datos_municipio['emision_residuos_ton'],
        datos_municipio['emision_industria_ton'],
        datos_municipio['emision_agricultura_ton']
    ]
    
    fig_bar = go.Figure(data=[
        go.Bar(
            x=categorias,
            y=valores,
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'],
            text=[f"{v:,.0f}" for v in valores],
            textposition='auto',
        )
    ])
    
    fig_bar.update_layout(
        title="Distribución de Emisiones (toneladas CO₂e/año)",
        xaxis_title="Categoría",
        yaxis_title="Toneladas CO₂e",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Gráfico de pastel
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = go.Figure(data=[go.Pie(
            labels=categorias,
            values=valores,
            hole=0.4,
            marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        )])
        
        fig_pie.update_layout(
            title="Proporción de Emisiones",
            height=350
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Indicadores adicionales
        st.markdown("### 🚗 Infraestructura")
        st.progress(datos_municipio['cobertura_transporte_publico_pct'] / 100)
        st.caption(f"Cobertura transporte público: {datos_municipio['cobertura_transporte_publico_pct']:.1f}%")
        
        st.progress(datos_municipio['vehiculos_particulares_pct'] / 100)
        st.caption(f"Vehículos particulares: {datos_municipio['vehiculos_particulares_pct']:.1f}%")

def mostrar_perfil(nombre_perfil):
    """Muestra la información del perfil asignado"""
    
    perfil = PERFILES[nombre_perfil]
    
    st.markdown(f"""
        <div class="perfil-card">
            <h2>{perfil['icono']} {nombre_perfil}</h2>
            <h3>📋 Descripción</h3>
    """, unsafe_allow_html=True)

    st.write(perfil['descripcion'])
    
    st.markdown(f"""
        <h3>💪 Motivación</h3>
        <p>{perfil['motivacion']}</p>
        
        <h3>👤 ¿A quién representa este perfil?</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar descripción ampliada fuera del HTML para mejor formato
    st.markdown(perfil['descripcion_ampliada'])

def generar_sugerencias(datos_municipio, perfil):
    """
    Genera sugerencias personalizadas usando el Motor de Inferencia.
    
    NUEVO: Ahora utiliza reglas de producción desde Firebase
    en lugar de lógica hardcodeada.
    """
    
    motor = inicializar_motor()
    motor.reiniciar()
    
    datos_usuario = {
        'municipio': datos_municipio['municipio'],
        'tipo_municipio': datos_municipio['tipo_municipio'],
        'nivel_contaminacion': datos_municipio['nivel_contaminacion'],
        'emision_industria_ton': datos_municipio['emision_industria_ton'],
        'perfil': perfil,
        'emision_per_capita_kg': datos_municipio['emision_per_capita_kg'],
        'actividades': [
            {
                'categoria': 'transporte',
                'sub_categoria': 'auto_gasolina',
                'cantidad': 30
            },
            {
                'categoria': 'energia',
                'sub_categoria': 'electricidad_red',
                'cantidad': 250
            }
        ]
    }
    
    motor.inicializar_hechos_desde_usuario(datos_usuario)
    
    try:
        motor.ejecutar_inferencia(max_iteraciones=10)
        sugerencias_inferidas = motor.obtener_sugerencias_formateadas()
        
        if not sugerencias_inferidas:
            sugerencias_inferidas = generar_sugerencias_clasicas(datos_municipio, perfil)
        
        return sugerencias_inferidas
    
    except Exception as e:
        st.error(f"Error en el motor de inferencia: {e}")
        return generar_sugerencias_clasicas(datos_municipio, perfil)

def generar_sugerencias_clasicas(datos_municipio, perfil):
    """Función original de sugerencias (como fallback)"""
    sugerencias = []
    
    emisiones = {
        'Transporte': datos_municipio['emision_transporte_ton'],
        'Energía': datos_municipio['emision_energia_ton'],
        'Residuos': datos_municipio['emision_residuos_ton'],
        'Industria': datos_municipio['emision_industria_ton'],
        'Agricultura': datos_municipio['emision_agricultura_ton']
    }
    
    categoria_mayor = max(emisiones, key=emisiones.get)
    
    if categoria_mayor == 'Transporte':
        if perfil == "El principiante":
            sugerencias.append("🚲 Intenta usar bicicleta o caminar para distancias cortas")
            sugerencias.append("🚌 Usa transporte público al menos 2 días a la semana")
        elif perfil == "El ecologista comprometido":
            sugerencias.append("🚗 Considera cambiar a un vehículo eléctrico o híbrido")
            sugerencias.append("🚴‍♂️ Implementa un plan de movilidad sostenible")
        else:
            sugerencias.append("👨‍👩‍👧 Organiza carpools con otras familias")
    
    elif categoria_mayor == 'Energía':
        if perfil == "El principiante":
            sugerencias.append("💡 Cambia a focos LED en toda la casa")
            sugerencias.append("❄️ Ajusta el termostato del AC 2°C más alto")
        elif perfil == "El ecologista comprometido":
            sugerencias.append("☀️ Instala paneles solares")
            sugerencias.append("🔌 Implementa sistema de monitoreo energético")
        else:
            sugerencias.append("👨‍👩‍👧‍👦 Establece horarios familiares para apagar dispositivos")
    
    return sugerencias

def calcular_comparativa(df, municipio_seleccionado):
    """Muestra comparativa del municipio con promedios estatales"""
    
    datos_muni = df[df['municipio'] == municipio_seleccionado].iloc[0]
    promedio_estatal = df['emision_per_capita_kg'].mean()
    diferencia = ((datos_muni['emision_per_capita_kg'] / promedio_estatal) - 1) * 100
    
    st.subheader("📊 Comparativa con Hidalgo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Tu municipio",
            f"{datos_muni['emision_per_capita_kg']:,.0f} kg CO₂e",
            delta=f"{diferencia:+.1f}% vs promedio estatal"
        )
    
    with col2:
        st.metric(
            "Promedio Hidalgo",
            f"{promedio_estatal:,.0f} kg CO₂e",
            delta=None
        )
    
    fig = go.Figure()
    top10 = df.nlargest(10, 'emision_per_capita_kg')
    
    colors = ['#FF6B6B' if m == municipio_seleccionado else '#4ECDC4' 
              for m in top10['municipio']]
    
    fig.add_trace(go.Bar(
        x=top10['emision_per_capita_kg'],
        y=top10['municipio'],
        orientation='h',
        marker_color=colors,
        text=top10['emision_per_capita_kg'].round(0),
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Top 10 Municipios con Mayor Emisión Per Cápita",
        xaxis_title="kg CO₂e por persona/año",
        yaxis_title="",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ===== FUNCIÓN PARA TAB SISTEMA DE REGLAS =====
def agregar_tab_sistema_reglas():
    """Nueva pestaña que muestra el sistema de reglas en acción"""
    
    st.markdown("## 🧠 Sistema de Inferencia Basado en Reglas")
    
    st.info("""
        **Sistema de Producción (Forward Chaining)**
        
        Este sistema utiliza **reglas de producción** almacenadas en Firebase
        para inferir sugerencias personalizadas basadas en tus datos.
        
        **Arquitectura:**
        - 📚 Base de Conocimientos (Firebase)
        - 🧠 Motor de Inferencia (Encadenamiento hacia adelante)
        - 💾 Memoria de Trabajo (Hechos del usuario)
    """)
    
    st.markdown("---")
    
    # Mostrar hechos actuales
    st.subheader("📝 Hechos en Memoria de Trabajo")
    
    motor = inicializar_motor()
    
    if motor.memoria_trabajo.hechos:
        hechos_data = []
        for hecho in motor.memoria_trabajo.hechos:
            hechos_data.append({
                'Tipo': hecho.tipo,
                'Atributo': hecho.atributo,
                'Valor': str(hecho.valor),
                'Confianza': f"{hecho.confianza:.2f}"
            })
        
        df_hechos = pd.DataFrame(hechos_data)
        st.dataframe(df_hechos, use_container_width=True)
    else:
        st.warning("⚠️ No hay hechos en memoria. Selecciona un municipio para comenzar.")
    
    st.markdown("---")
    
    # Mostrar reglas cargadas
    st.subheader("📚 Reglas de Producción Activas")
    
    if motor.reglas:
        grupos = list(motor.reglas.keys())
        grupo_seleccionado = st.selectbox("Selecciona grupo de reglas:", grupos)
        
        if grupo_seleccionado:
            reglas_grupo = motor.reglas[grupo_seleccionado]
            
            st.markdown(f"**{len(reglas_grupo)} reglas en este grupo**")
            
            for regla_id, regla in reglas_grupo.items():
                with st.expander(f"🔹 {regla['nombre']} (Prioridad: {regla['prioridad']})"):
                    st.markdown("**Condiciones:**")
                    st.json(regla['condiciones'])
                    
                    st.markdown("**Conclusión:**")
                    st.json(regla['conclusion'])
    else:
        st.error("❌ No se pudieron cargar las reglas desde Firebase")
    
    st.markdown("---")
    
    # Mostrar conclusiones/inferencias
    st.subheader("🎯 Conclusiones Inferidas")
    
    if motor.conclusiones:
        for i, conclusion in enumerate(motor.conclusiones, 1):
            st.markdown(f"""
                <div style='background-color: #E8F5E9; padding: 15px; 
                           border-radius: 10px; margin: 10px 0;
                           border-left: 5px solid #4CAF50;'>
                    <strong>Inferencia {i}:</strong> {conclusion['regla']}<br>
                    <strong>Prioridad:</strong> {conclusion['prioridad']}<br>
                    <strong>Resultado:</strong> {conclusion['conclusion']}
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ No hay inferencias aún. El motor se ejecutará cuando selecciones un municipio.")
    
    st.markdown("---")
    
    # Botones de control
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Recargar Reglas desde Firebase", use_container_width=True):
            motor.cargar_reglas()
            st.success("✅ Reglas recargadas correctamente")
            st.rerun()
    
    with col2:
        if st.button("🧹 Limpiar Memoria de Trabajo", use_container_width=True):
            motor.reiniciar()
            st.success("✅ Memoria limpiada")
            st.rerun()
    
    # Documentación técnica
    with st.expander("📖 Documentación Técnica"):
        st.markdown("""
        ### Paradigma Lógico Implementado
        
        **1. Base de Conocimientos:**
        - Reglas de producción en formato: SI <condiciones> ENTONCES <conclusión>
        - Almacenadas en Firebase Realtime Database
        - Actualizables en tiempo real sin modificar código
        
        **2. Motor de Inferencia:**
        - **Tipo:** Encadenamiento hacia adelante (Forward Chaining)
        - **Algoritmo:** MATCH-RESOLVE-EXECUTE
        - **Búsqueda:** Sistemática sobre espacio de hechos
        
        **3. Memoria de Trabajo:**
        - Almacena hechos (proposiciones verdaderas)
        - Se actualiza dinámicamente durante la inferencia
        - Permite razonamiento incremental
        
        **4. Resolución de Conflictos:**
        - Criterio: Mayor prioridad primero
        - Evita disparo múltiple de la misma regla
        - Límite de iteraciones para prevenir loops infinitos
        
        ### Buenas Prácticas Aplicadas
        
        ✅ **Separación de Conocimiento y Control:**
        - Reglas separadas del código (Firebase)
        - Motor de inferencia reutilizable
        
        ✅ **Modularidad:**
        - Clases independientes (Hecho, MemoriaTrabajo, MotorInferencia)
        - Principio de Responsabilidad Única
        
        ✅ **Programación Funcional:**
        - Uso de filter(), map(), reduce()
        - Funciones puras sin efectos secundarios
        
        ✅ **Manejo de Errores:**
        - Fallback a reglas por defecto si Firebase falla
        - Try-catch en todas las operaciones críticas
        
        ✅ **Documentación:**
        - Docstrings en todas las funciones
        - Comentarios explicando reglas de negocio
        """)

# ===== APLICACIÓN PRINCIPAL =====
def main():
    # Header
    st.markdown('<h1 class="main-header">🌱 Calculadora de Huella de Carbono - Hidalgo</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
        <div style='text-align: center; padding: 1rem; background-color: #E8F5E9; border-radius: 10px; margin-bottom: 2rem;'>
            <p style='font-size: 1.1rem; color: #2E7D32;'>
                <strong>ODS 13: Acción por el Clima</strong> | 
                Conoce el impacto ambiental de tu municipio y recibe recomendaciones personalizadas
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    df = cargar_datos()
    
    # Sidebar para selección
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/4CAF50/FFFFFF?text=Huella+de+Carbono", 
                 use_container_width=True)
        
        # Estado de conexión Firebase
        st.markdown("---")
        st.markdown("### 🔥 Sistema de Reglas")
        
        firebase = FirebaseConnection()
        if firebase.db_ref:
            st.success("✅ Conectado a Firebase")
            
            # Botón para recargar reglas
            if st.button("🔄 Recargar Reglas", use_container_width=True):
                motor = inicializar_motor()
                motor.cargar_reglas()
                st.success("Reglas actualizadas")
        else:
            st.error("❌ Sin conexión a Firebase")
            with st.expander("ℹ️ Configurar Firebase"):
                st.info("""
                1. Descarga credenciales desde Firebase Console
                2. Guárdalas como 'firebase-credentials.json'
                3. Reinicia la aplicación
                """)
        
        st.markdown("---")
        st.markdown("## 🏠 Selecciona tu Municipio")
        
        # Filtros
        tipo_filtro = st.selectbox(
            "Filtrar por tipo:",
            ["Todos"] + sorted(df['tipo_municipio'].unique().tolist())
        )
        
        if tipo_filtro != "Todos":
            municipios_filtrados = df[df['tipo_municipio'] == tipo_filtro]['municipio'].sort_values().tolist()
        else:
            municipios_filtrados = df['municipio'].sort_values().tolist()
        
        municipio_seleccionado = st.selectbox(
            "Municipio:",
            municipios_filtrados,
            index=0
        )
        
        st.markdown("---")
        
        # Información rápida
        if municipio_seleccionado:
            datos = df[df['municipio'] == municipio_seleccionado].iloc[0]
            st.markdown(f"""
                ### 📌 Info Rápida
                **Tipo:** {datos['tipo_municipio']}  
                **Población:** {datos['poblacion']:,}  
                **Nivel:** {datos['nivel_contaminacion']}
            """)
        
        st.markdown("---")
        st.markdown("### 📚 Acerca de")
        st.info("Este sistema calcula la huella de carbono basándose en datos de los 84 municipios de Hidalgo y asigna perfiles de usuario personalizados.")
    
    # Contenido principal
    if municipio_seleccionado:
        datos_municipio = df[df['municipio'] == municipio_seleccionado].iloc[0]
        
        # Tabs para organizar contenido
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🗺️ Mapa y Datos", 
            "👤 Tu Perfil", 
            "💡 Sugerencias",
            "📊 Análisis Detallado",
            "🧠 Sistema de Reglas"
        ])
        
        with tab1:
            niveles_seleccionados = crear_panel_filtros(df)
            st.markdown("---")
            
            fig_mapa = crear_mapa_con_filtros(df, niveles_seleccionados, municipio_seleccionado)
            
            if fig_mapa:
                st.plotly_chart(fig_mapa, use_container_width=True)
                
                col_info1, col_info2 = st.columns(2)
                
                with col_info1:
                    st.info("""
                        **💡 Tip de navegación:**
                        - Haz zoom con la rueda del mouse
                        - Arrastra para moverte por el mapa
                        - Pasa el mouse sobre los círculos para ver detalles
                        - Haz clic en la leyenda para ocultar/mostrar niveles
                    """)
                
                with col_info2:
                    st.success("""
                        **🎯 Coordenadas verificadas:**
                        - Todas las ubicaciones son exactas según INEGI
                        - Los círculos representan las cabeceras municipales
                        - El tamaño es proporcional a la emisión per cápita
                    """)
                
                crear_tabla_municipios_filtrados(df, niveles_seleccionados)
                
            st.markdown("---")
            mostrar_info_municipio(datos_municipio)
        
        with tab2:
            st.subheader("👤 Tu Perfil de Usuario")
            perfil_asignado = datos_municipio['perfil_predominante']
            
            st.info(f"""
                **Basándonos en las características de {municipio_seleccionado}**,
                el perfil que mejor se adapta a tu contexto es:
            """)
            
            mostrar_perfil(perfil_asignado)
        
        with tab3:
            st.markdown("## 💡 Recomendaciones Personalizadas")
            perfil_actual = datos_municipio['perfil_predominante']
            
            sugerencias = generar_sugerencias(datos_municipio, perfil_actual)
            
            st.markdown(f"""
                <div style='background-color: #FFF3E0; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #FF9800;'>
                    <h3>📋 Sugerencias para {perfil_actual}</h3>
                    <p>Basadas en el perfil <strong>{datos_municipio['nivel_contaminacion']}</strong> 
                    de contaminación de tu municipio</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            for i, sugerencia in enumerate(sugerencias, 1):
                st.markdown(f"""
                    <div class="metric-card">
                        <h4>{i}. {sugerencia}</h4>
                    </div>
                """, unsafe_allow_html=True)
            
            # Estimación de impacto
            st.markdown("---")
            st.markdown("### 🎯 Impacto Potencial")
            
            col1, col2, col3 = st.columns(3)
            
            reduccion_estimada = np.random.uniform(10, 30)
            
            with col1:
                st.metric(
                    "Reducción Potencial",
                    f"{reduccion_estimada:.0f}%",
                    delta=f"-{datos_municipio['emision_per_capita_kg'] * reduccion_estimada / 100:.0f} kg CO₂e/año"
                )
            
            with col2:
                arboles_equivalentes = (datos_municipio['emision_per_capita_kg'] * reduccion_estimada / 100) / 20
                st.metric(
                    "Equivalente a",
                    f"{arboles_equivalentes:.0f} árboles",
                    delta="plantados al año"
                )
            
            with col3:
                ahorro_economico = (datos_municipio['emision_per_capita_kg'] * reduccion_estimada / 100) * 0.5
                st.metric(
                    "Ahorro Estimado",
                    f"${ahorro_economico:.0f} MXN",
                    delta="por año"
                )
        
        with tab4:
            st.markdown("## 📊 Análisis Detallado")
            
            calcular_comparativa(df, municipio_seleccionado)
            
            st.markdown("---")
            
            # Estadísticas avanzadas
            st.subheader("📈 Estadísticas del Estado")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Municipio más contaminante",
                    df.nlargest(1, 'emision_per_capita_kg')['municipio'].values[0],
                    delta=f"{df['emision_per_capita_kg'].max():,.0f} kg CO₂e"
                )
            
            with col2:
                st.metric(
                    "Municipio más limpio",
                    df.nsmallest(1, 'emision_per_capita_kg')['municipio'].values[0],
                    delta=f"{df['emision_per_capita_kg'].min():,.0f} kg CO₂e"
                )
            
            with col3:
                st.metric(
                    "Emisión total Hidalgo",
                    f"{df['emision_total_ton'].sum()/1000:.0f} mil ton",
                    delta=None
                )
            
            # Distribución por tipo
            st.markdown("---")
            st.subheader("🏭 Distribución por Tipo de Municipio")
            
            tipo_stats = df.groupby('tipo_municipio').agg({
                'emision_per_capita_kg': 'mean',
                'poblacion': 'sum',
                'municipio': 'count'
            }).reset_index()
            
            fig_tipo = go.Figure()
            
            fig_tipo.add_trace(go.Bar(
                x=tipo_stats['tipo_municipio'],
                y=tipo_stats['emision_per_capita_kg'],
                name='Emisión per cápita promedio',
                marker_color='#FF6B6B',
                yaxis='y',
                text=tipo_stats['emision_per_capita_kg'].round(0),
                textposition='auto'
            ))
            
            fig_tipo.add_trace(go.Scatter(
                x=tipo_stats['tipo_municipio'],
                y=tipo_stats['municipio'],
                name='Número de municipios',
                marker_color='#4ECDC4',
                yaxis='y2',
                mode='lines+markers+text',
                text=tipo_stats['municipio'],
                textposition='top center'
            ))
            
            fig_tipo.update_layout(
                title='Comparativa por Tipo de Municipio',
                xaxis_title='Tipo',
                yaxis_title='kg CO₂e per cápita',
                yaxis2=dict(
                    title='Número de municipios',
                    overlaying='y',
                    side='right'
                ),
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_tipo, use_container_width=True)
        
        with tab5:
            agregar_tab_sistema_reglas()
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 2rem;'>
            <p>🌍 <strong>Proyecto: Calculadora de Huella de Carbono Personal</strong></p>
            <p>Desarrollado con Python, Streamlit y Plotly | ODS 13: Acción por el Clima</p>
            <p style='font-size: 0.9rem;'>Datos sintéticos basados en información real de Hidalgo, México</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()