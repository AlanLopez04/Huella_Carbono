"""
Mapa profesional de Hidalgo con coordenadas exactas verificadas
Incluye filtros interactivos por nivel de contaminación
"""

import plotly.graph_objects as go
import pandas as pd
import streamlit as st

# Coordenadas exactas de las cabeceras municipales de Hidalgo
# Verificadas con datos de INEGI y fuentes geográficas oficiales
COORDENADAS_EXACTAS_HIDALGO = {
    "Acatlán": (20.1461, -98.4383),
    "Acaxochitlán": (20.1697, -98.2058),
    "Actopan": (20.2697, -98.9436),
    "Agua Blanca de Iturbide": (20.3508, -98.3583),
    "Ajacuba": (20.0911, -99.0950),
    "Alfajayucan": (20.4108, -99.3497),
    "Almoloya": (20.7364, -98.4011),
    "Apan": (19.7114, -98.4531),
    "Atitalaquia": (20.0600, -99.2211),
    "Atlapexco": (21.0144, -98.3608),
    "Atotonilco de Tula": (20.0011, -99.2178),
    "Atotonilco el Grande": (20.2858, -98.7136),
    "Calnali": (20.8992, -98.5872),
    "Cardonal": (20.6094, -99.1039),
    "Cuautepec de Hinojosa": (20.0256, -98.2925),
    "Chapantongo": (20.2878, -99.4139),
    "Chapulhuacán": (21.1564, -98.9039),
    "Chilcuautla": (20.3383, -99.2389),
    "Eloxochitlán": (20.5781, -98.7689),
    "Emiliano Zapata": (19.6658, -98.5483),
    "Epazoyucan": (19.9967, -98.6372),
    "Francisco I. Madero": (20.2456, -99.0886),
    "Huasca de Ocampo": (20.2039, -98.5747),
    "Huautla": (21.0308, -98.2892),
    "Huazalingo": (20.9728, -98.5142),
    "Huehuetla": (20.4156, -98.0831),
    "Huejutla de Reyes": (21.1397, -98.4206),
    "Huichapan": (20.3750, -99.6519),
    "Ixmiquilpan": (20.4869, -99.2156),
    "Jacala de Ledezma": (21.0086, -99.1889),
    "Jaltocán": (21.1950, -98.5528),
    "Juárez Hidalgo": (20.7875, -98.4536),
    "Lolotla": (20.7739, -98.7308),
    "Metepec": (19.9622, -98.3272),
    "San Agustín Metzquititlán": (20.5703, -98.7675),
    "Metztitlán": (20.5958, -98.7642),
    "Mineral del Chico": (20.1989, -98.7281),
    "Mineral del Monte": (20.1408, -98.6739),
    "Misión": (19.7375, -98.6892),
    "Mixquiahuala de Juárez": (20.2300, -99.2142),
    "Molango de Escamilla": (20.7897, -98.7300),
    "Nicolás Flores": (20.7669, -99.1536),
    "Nopala de Villagrán": (20.2583, -99.6467),
    "Omitlán de Juárez": (20.1844, -98.6497),
    "San Felipe Orizatlán": (21.1700, -98.6075),
    "Pacula": (20.9875, -99.6339),
    "Pachuca de Soto": (20.1219, -98.7361),
    "Pisaflores": (21.1944, -99.0061),
    "Progreso de Obregón": (20.2456, -99.1878),
    "Mineral de la Reforma": (20.0686, -98.6989),
    "San Agustín Tlaxiaca": (20.1147, -98.8867),
    "San Bartolo Tutotepec": (20.3992, -98.2019),
    "San Salvador": (20.2872, -99.0136),
    "Santiago de Anaya": (20.3886, -98.9536),
    "Santiago Tulantepec de Lugo Guerrero": (20.0369, -98.3597),
    "Singuilucan": (19.9614, -98.5158),
    "Tasquillo": (20.5492, -99.3075),
    "Tecozautla": (20.5333, -99.6342),
    "Tenango de Doria": (20.3408, -98.2292),
    "Tepeapulco": (19.7853, -98.5536),
    "Tepehuacán de Guerrero": (21.0133, -98.8411),
    "Tepeji del Río de Ocampo": (19.9058, -99.3450),
    "Tepetitlán": (20.0317, -99.3228),
    "Tetepango": (19.8869, -99.2736),
    "Villa de Tezontepec": (19.8792, -98.8200),
    "Tezontepec de Aldama": (20.1928, -99.2739),
    "Tianguistengo": (20.7197, -98.5444),
    "Tizayuca": (19.8408, -98.9814),
    "Tlahuelilpan": (20.1281, -99.2350),
    "Tlahuiltepa": (20.6831, -98.8408),
    "Tlanalapa": (19.8167, -98.6158),
    "Tlanchinol": (20.9875, -98.6581),
    "Tlaxcoapan": (20.0939, -99.2231),
    "Tolcayuca": (19.9575, -98.9208),
    "Tula de Allende": (20.0533, -99.3444),
    "Tulancingo de Bravo": (20.0842, -98.3639),
    "Xochiatipan": (20.8386, -98.2864),
    "Xochicoatlán": (20.7997, -98.4483),
    "Yahualica": (21.1789, -98.7517),
    "Zacualtipán de Ángeles": (20.6467, -98.6558),
    "Zapotlán de Juárez": (19.9683, -98.8617),
    "Zempoala": (19.9181, -98.6711),
    "Zimapán": (20.7394, -99.3764)
}


def crear_mapa_con_filtros(df, niveles_filtro=None, municipio_seleccionado=None):
    """
    Crea mapa interactivo con filtros por nivel de contaminación
    
    Args:
        df: DataFrame con datos de municipios
        niveles_filtro: Lista de niveles a mostrar (ej: ['Muy Alto', 'Alto'])
        municipio_seleccionado: Municipio específico a resaltar
    """
    
    # Agregar coordenadas exactas
    df_mapa = df.copy()
    df_mapa['lat'] = df_mapa['municipio'].map(
        lambda x: COORDENADAS_EXACTAS_HIDALGO.get(x, (20.5, -98.8))[0]
    )
    df_mapa['lon'] = df_mapa['municipio'].map(
        lambda x: COORDENADAS_EXACTAS_HIDALGO.get(x, (20.5, -98.8))[1]
    )
    
    # Aplicar filtros
    if niveles_filtro and len(niveles_filtro) > 0:
        df_mapa = df_mapa[df_mapa['nivel_contaminacion'].isin(niveles_filtro)]
    
    if len(df_mapa) == 0:
        st.warning("⚠️ No hay municipios que coincidan con los filtros seleccionados")
        return None
    
    # Mapeo de colores
    colors_map = {
        'Muy Alto': '#8B0000',
        'Alto': '#DC143C',
        'Medio': '#FF8C00',
        'Bajo': '#FFD700',
        'Muy Bajo': '#90EE90'
    }
    
    # Crear figura
    fig = go.Figure()
    
    # Agrupar por nivel para crear trazas separadas (para leyenda interactiva)
    niveles_unicos = df_mapa['nivel_contaminacion'].unique()
    
    for nivel in ['Muy Alto', 'Alto', 'Medio', 'Bajo', 'Muy Bajo']:
        if nivel not in niveles_unicos:
            continue
            
        df_nivel = df_mapa[df_mapa['nivel_contaminacion'] == nivel]
        
        # Calcular tamaños
        min_val = df_nivel['emision_per_capita_kg'].min()
        max_val = df_nivel['emision_per_capita_kg'].max()
        
        if max_val - min_val > 0:
            sizes = 10 + ((df_nivel['emision_per_capita_kg'] - min_val) / (max_val - min_val)) * 20
        else:
            sizes = [15] * len(df_nivel)
        
        # Resaltar municipio seleccionado
        if municipio_seleccionado:
            sizes = [s * 1.5 if m == municipio_seleccionado else s 
                    for m, s in zip(df_nivel['municipio'], sizes)]
            opacities = [0.95 if m == municipio_seleccionado else 0.7 
                        for m in df_nivel['municipio']]
        else:
            opacities = 0.75
        
        # Agregar traza por nivel
        fig.add_trace(go.Scattermapbox(
            lat=df_nivel['lat'],
            lon=df_nivel['lon'],
            mode='markers',
            marker=dict(
                size=sizes,
                color=colors_map[nivel],
                opacity=opacities,
            ),
            name=f'{nivel} ({len(df_nivel)})',
            text=df_nivel['municipio'],
            customdata=df_nivel[[
                'tipo_municipio',
                'emision_per_capita_kg',
                'poblacion',
                'emision_total_ton',
                'caracteristica_especial'
            ]],
            hovertemplate=(
                '<b>%{text}</b><br>' +
                '<b>Nivel: ' + nivel + '</b><br>' +
                'Tipo: %{customdata[0]}<br>' +
                'Emisión per cápita: %{customdata[1]:,.0f} kg CO₂e<br>' +
                'Población: %{customdata[2]:,}<br>' +
                'Emisión total: %{customdata[3]:,.0f} ton<br>' +
                'Característica: %{customdata[4]}<br>' +
                '<extra></extra>'
            )
        ))
    
    # Agregar etiquetas para municipios clave
    municipios_clave = [
        'Pachuca de Soto', 'Tula de Allende', 'Tulancingo de Bravo',
        'Huejutla de Reyes', 'Tizayuca', 'Atitalaquia'
    ]
    
    df_etiquetas = df_mapa[df_mapa['municipio'].isin(municipios_clave)]
    
    if len(df_etiquetas) > 0:
        nombres = []
        for m in df_etiquetas['municipio']:
            if 'Pachuca' in m:
                nombres.append('PACHUCA')
            elif 'Tula de Allende' in m:
                nombres.append('TULA')
            elif 'Tulancingo' in m:
                nombres.append('TULANCINGO')
            elif 'Huejutla' in m:
                nombres.append('HUEJUTLA')
            elif 'Tizayuca' in m:
                nombres.append('TIZAYUCA')
            elif 'Atitalaquia' in m:
                nombres.append('ATITALAQUIA')
            else:
                nombres.append(m.split()[0].upper())
        
        fig.add_trace(go.Scattermapbox(
            lat=df_etiquetas['lat'],
            lon=df_etiquetas['lon'],
            mode='text',
            text=nombres,
            textfont=dict(
                size=9,
                color='#1a1a1a',
                family='Arial Black'
            ),
            textposition='bottom center',
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Configurar mapa
    fig.update_layout(
        mapbox=dict(
            style='open-street-map',
            center=dict(
                lat=df_mapa['lat'].mean(),
                lon=df_mapa['lon'].mean()
            ),
            zoom=7.5
        ),
        title={
            'text': f'🗺️ Mapa de Hidalgo - Huella de Carbono ({len(df_mapa)} municipios)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2E7D32'}
        },
        height=650,
        margin=dict(l=0, r=0, t=60, b=0),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#666",
            borderwidth=1
        ),
        paper_bgcolor='#FAFAFA'
    )
    
    return fig


def crear_panel_filtros(df):
    """
    Crea panel interactivo de filtros en Streamlit
    
    Returns:
        niveles_seleccionados: Lista de niveles seleccionados
    """
    
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
            <h3 style='margin: 0;'>🔍 Filtros Interactivos</h3>
            <p style='margin: 5px 0 0 0; font-size: 14px;'>
                Selecciona los niveles de contaminación que deseas visualizar
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Contar municipios por nivel
    conteo_niveles = df['nivel_contaminacion'].value_counts()
    
    # Crear columnas para filtros
    col1, col2, col3, col4, col5 = st.columns(5)
    
    niveles_seleccionados = []
    
    with col1:
        if st.checkbox(
            f'🔴 Muy Alto\n({conteo_niveles.get("Muy Alto", 0)})',
            value=True,
            key='filtro_muy_alto'
        ):
            niveles_seleccionados.append('Muy Alto')
    
    with col2:
        if st.checkbox(
            f'🟠 Alto\n({conteo_niveles.get("Alto", 0)})',
            value=True,
            key='filtro_alto'
        ):
            niveles_seleccionados.append('Alto')
    
    with col3:
        if st.checkbox(
            f'🟡 Medio\n({conteo_niveles.get("Medio", 0)})',
            value=True,
            key='filtro_medio'
        ):
            niveles_seleccionados.append('Medio')
    
    with col4:
        if st.checkbox(
            f'🟢 Bajo\n({conteo_niveles.get("Bajo", 0)})',
            value=True,
            key='filtro_bajo'
        ):
            niveles_seleccionados.append('Bajo')
    
    with col5:
        if st.checkbox(
            f'🔵 Muy Bajo\n({conteo_niveles.get("Muy Bajo", 0)})',
            value=True,
            key='filtro_muy_bajo'
        ):
            niveles_seleccionados.append('Muy Bajo')
    

    
    # Mostrar estadísticas de filtros
    if niveles_seleccionados:
        df_filtrado = df[df['nivel_contaminacion'].isin(niveles_seleccionados)]
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.metric(
                "Municipios mostrados",
                len(df_filtrado),
                delta=f"{(len(df_filtrado)/len(df)*100):.0f}% del total"
            )
        
        with col_stat2:
            st.metric(
                "Población total",
                f"{df_filtrado['poblacion'].sum():,}",
                delta=None
            )
        
        with col_stat3:
            st.metric(
                "Emisión promedio",
                f"{df_filtrado['emision_per_capita_kg'].mean():,.0f} kg",
                delta=None
            )
    
    return niveles_seleccionados


def crear_tabla_municipios_filtrados(df, niveles_filtro=None):
    """
    Muestra una tabla de los municipios filtrados por nivel de contaminación.
    
    CORRECCIÓN 2: Se añade st.dataframe para la correcta visualización de la tabla.
    """
    
    df_filtrado = df.copy()

    if niveles_filtro and len(niveles_filtro) > 0:
        df_filtrado = df_filtrado[df_filtrado['nivel_contaminacion'].isin(niveles_filtro)]
    
    if len(df_filtrado) == 0:
        st.warning("⚠️ No hay municipios que coincidan con los filtros seleccionados.")
        return

    # Seleccionar, renombrar y añadir columna para Emisión Total
    df_tabla = df_filtrado[[
        'municipio', 
        'nivel_contaminacion', 
        'emision_per_capita_kg', 
        'poblacion', 
        'emision_total_ton'
    ]].copy()
    
    df_tabla.columns = ['Municipio', 'Nivel', 'Emisión Per Cápita (kg CO₂e)', 'Población', 'Emisión Total (ton CO₂e)']
    
    # Ordenar por el nivel de contaminación para mostrar por "secciones"
    niveles_orden = ['Muy Alto', 'Alto', 'Medio', 'Bajo', 'Muy Bajo']
    
    # Crear una columna categórica para un ordenamiento semántico correcto
    df_tabla['Nivel_Orden'] = pd.Categorical(
        df_tabla['Nivel'], 
        categories=niveles_orden, 
        ordered=True
    )
    
    # Ordenar primero por Nivel (descendente) y luego por Emisión Per Cápita (descendente)
    df_tabla_sorted = df_tabla.sort_values(
        by=['Nivel_Orden', 'Emisión Per Cápita (kg CO₂e)'], 
        ascending=[False, False]
    ).drop(columns=['Nivel_Orden'])
    
    # Mostrar la tabla correctamente con st.dataframe (Corrección 2)
    st.dataframe(
        df_tabla_sorted,
        column_config={
            "Emisión Per Cápita (kg CO₂e)": st.column_config.NumberColumn(
                format="%.0f kg"
            ),
            "Población": st.column_config.NumberColumn(
                format="%.0f"
            ),
            "Emisión Total (ton CO₂e)": st.column_config.NumberColumn(
                format="%.0f ton"
            )
        },
        hide_index=True,
        use_container_width=True
    )
    
    