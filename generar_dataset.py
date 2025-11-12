import pandas as pd
import numpy as np
import random
from datetime import datetime

# Configurar semilla para reproducibilidad
np.random.seed(42)
random.seed(42)

# Lista completa de los 84 municipios de Hidalgo
municipios_hidalgo = [
    "Acatlán", "Acaxochitlán", "Actopan", "Agua Blanca de Iturbide", "Ajacuba",
    "Alfajayucan", "Almoloya", "Apan", "Atitalaquia", "Atlapexco",
    "Atotonilco de Tula", "Atotonilco el Grande", "Calnali", "Cardonal", "Cuautepec de Hinojosa",
    "Chapantongo", "Chapulhuacán", "Chilcuautla", "Eloxochitlán", "Emiliano Zapata",
    "Epazoyucan", "Francisco I. Madero", "Huasca de Ocampo", "Huautla", "Huazalingo",
    "Huehuetla", "Huejutla de Reyes", "Huichapan", "Ixmiquilpan", "Jacala de Ledezma",
    "Jaltocán", "Juárez Hidalgo", "Lolotla", "Metepec", "San Agustín Metzquititlán",
    "Metztitlán", "Mineral del Chico", "Mineral del Monte", "Misión", "Mixquiahuala de Juárez",
    "Molango de Escamilla", "Nicolás Flores", "Nopala de Villagrán", "Omitlán de Juárez", "San Felipe Orizatlán",
    "Pacula", "Pachuca de Soto", "Pisaflores", "Progreso de Obregón", "Mineral de la Reforma",
    "San Agustín Tlaxiaca", "San Bartolo Tutotepec", "San Salvador", "Santiago de Anaya", "Santiago Tulantepec de Lugo Guerrero",
    "Singuilucan", "Tasquillo", "Tecozautla", "Tenango de Doria", "Tepeapulco",
    "Tepehuacán de Guerrero", "Tepeji del Río de Ocampo", "Tepetitlán", "Tetepango", "Villa de Tezontepec",
    "Tezontepec de Aldama", "Tianguistengo", "Tizayuca", "Tlahuelilpan", "Tlahuiltepa",
    "Tlanalapa", "Tlanchinol", "Tlaxcoapan", "Tolcayuca", "Tula de Allende",
    "Tulancingo de Bravo", "Xochiatipan", "Xochicoatlán", "Yahualica", "Zacualtipán de Ángeles",
    "Zapotlán de Juárez", "Zempoala", "Zimapán"
]

# Municipios con alta actividad industrial (refinería, termoeléctricas, parques industriales)
municipios_alta_industria = {
    "Tula de Allende": "refinería_termoelectrica",  # Refinería Miguel Hidalgo + Termoeléctrica
    "Atitalaquia": "corredor_industrial",  # Corredor industrial Tula-Tepeji
    "Atotonilco de Tula": "corredor_industrial",  # Parte del corredor industrial
    "Tepeji del Río de Ocampo": "parque_industrial",  # Múltiples parques industriales
    "Tizayuca": "parque_industrial_logistica",  # Mayor parque industrial de Hidalgo (88 empresas)
}

# Municipios con actividad minera
municipios_mineros = ["Zimapán", "Mineral del Monte", "Mineral del Chico", "Molango de Escamilla", 
                      "Cardonal", "Jacala de Ledezma"]

# Municipios urbanos principales
municipios_urbanos = ["Pachuca de Soto", "Tulancingo de Bravo", "Mineral de la Reforma"]

# Municipios semiurbanos
municipios_semiurbanos = [
    "Actopan", "Apan", "Huejutla de Reyes", "Ixmiquilpan", "Mixquiahuala de Juárez",
    "Tepeapulco", "Cuautepec de Hinojosa", "Huichapan", "Santiago Tulantepec de Lugo Guerrero", 
    "Zempoala", "Tlahuelilpan", "Tepetitlán"
]

def generar_datos_municipio(municipio):
    """Genera datos sintéticos realistas para un municipio basado en información real"""
    
    # Determinar tipo y características especiales
    tipo_industria = None
    if municipio in municipios_alta_industria:
        tipo = "Industrial Pesado"
        tipo_industria = municipios_alta_industria[municipio]
    elif municipio in municipios_mineros:
        tipo = "Minero"
        tipo_industria = "mineria"
    elif municipio in municipios_urbanos:
        tipo = "Urbano"
    elif municipio in municipios_semiurbanos:
        tipo = "Semiurbano"
    else:
        tipo = "Rural"
    
    # Población realista según tipo
    if tipo == "Industrial Pesado":
        poblacion = np.random.randint(50000, 120000)
        densidad_poblacional = np.random.randint(800, 2500)
    elif tipo == "Urbano":
        if municipio == "Pachuca de Soto":
            poblacion = np.random.randint(250000, 300000)
        else:
            poblacion = np.random.randint(100000, 200000)
        densidad_poblacional = np.random.randint(2000, 6000)
    elif tipo == "Semiurbano":
        poblacion = np.random.randint(20000, 80000)
        densidad_poblacional = np.random.randint(400, 1500)
    elif tipo == "Minero":
        poblacion = np.random.randint(8000, 40000)
        densidad_poblacional = np.random.randint(100, 800)
    else:  # Rural
        poblacion = np.random.randint(3000, 25000)
        densidad_poblacional = np.random.randint(40, 400)
    
    # EMISIONES REALISTAS basadas en datos reales
    # Tula emite ~136,000 ton de SO2 + otras emisiones
    
    if municipio == "Tula de Allende":
        # Refinería + Termoeléctrica = emisiones extremadamente altas
        emision_industria = np.random.uniform(180000, 220000)  # La mayor del estado
        emision_energia = np.random.uniform(80000, 120000)  # Termoeléctricas
        emision_transporte = np.random.uniform(20000, 35000)
        emision_residuos = np.random.uniform(8000, 15000)
        emision_agricultura = np.random.uniform(2000, 5000)
        
    elif municipio == "Atitalaquia":
        # Corredor industrial Tula-Tepeji, muy contaminado
        emision_industria = np.random.uniform(80000, 120000)
        emision_energia = np.random.uniform(30000, 50000)
        emision_transporte = np.random.uniform(15000, 25000)
        emision_residuos = np.random.uniform(5000, 10000)
        emision_agricultura = np.random.uniform(1500, 4000)
        
    elif municipio == "Atotonilco de Tula":
        # Parte del corredor industrial
        emision_industria = np.random.uniform(60000, 90000)
        emision_energia = np.random.uniform(25000, 40000)
        emision_transporte = np.random.uniform(12000, 20000)
        emision_residuos = np.random.uniform(4000, 8000)
        emision_agricultura = np.random.uniform(1500, 3500)
        
    elif municipio == "Tepeji del Río de Ocampo":
        # Múltiples parques industriales
        emision_industria = np.random.uniform(50000, 80000)
        emision_energia = np.random.uniform(20000, 35000)
        emision_transporte = np.random.uniform(15000, 25000)
        emision_residuos = np.random.uniform(5000, 10000)
        emision_agricultura = np.random.uniform(1000, 3000)
        
    elif municipio == "Tizayuca":
        # Mayor parque industrial (88 empresas) + logística
        emision_industria = np.random.uniform(45000, 75000)
        emision_energia = np.random.uniform(18000, 30000)
        emision_transporte = np.random.uniform(20000, 35000)  # Alta por logística
        emision_residuos = np.random.uniform(6000, 12000)
        emision_agricultura = np.random.uniform(1000, 2500)
        
    elif municipio == "Tepetitlán":
        # Presa Endhó (novena fuente de GEI del estado)
        emision_industria = np.random.uniform(5000, 12000)
        emision_energia = np.random.uniform(3000, 8000)
        emision_transporte = np.random.uniform(2000, 5000)
        emision_residuos = np.random.uniform(8000, 15000)  # Alta por presa de aguas negras
        emision_agricultura = np.random.uniform(3000, 7000)
        
    elif tipo == "Minero":
        emision_industria = np.random.uniform(15000, 40000)  # Extracción y procesamiento
        emision_energia = np.random.uniform(8000, 20000)
        emision_transporte = np.random.uniform(5000, 12000)
        emision_residuos = np.random.uniform(2000, 6000)
        emision_agricultura = np.random.uniform(800, 2500)
        
    elif tipo == "Urbano":
        emision_transporte = np.random.uniform(25000, 50000)
        emision_energia = np.random.uniform(30000, 60000)
        emision_residuos = np.random.uniform(8000, 18000)
        emision_industria = np.random.uniform(8000, 20000)
        emision_agricultura = np.random.uniform(500, 2000)
        
    elif tipo == "Semiurbano":
        emision_transporte = np.random.uniform(8000, 18000)
        emision_energia = np.random.uniform(10000, 25000)
        emision_residuos = np.random.uniform(3000, 8000)
        emision_industria = np.random.uniform(4000, 15000)
        emision_agricultura = np.random.uniform(2000, 6000)
        
    else:  # Rural
        emision_transporte = np.random.uniform(1500, 6000)
        emision_energia = np.random.uniform(2500, 8000)
        emision_residuos = np.random.uniform(800, 3000)
        emision_industria = np.random.uniform(500, 3000)
        emision_agricultura = np.random.uniform(4000, 12000)  # Alta en zonas rurales
    
    emision_total = emision_transporte + emision_energia + emision_residuos + emision_industria + emision_agricultura
    emision_per_capita = (emision_total / poblacion) * 1000  # kg CO2e por persona
    
    # Datos socioeconómicos
    if tipo == "Industrial Pesado":
        nivel_ingreso_promedio = np.random.uniform(7000, 12000)
    elif tipo == "Urbano":
        nivel_ingreso_promedio = np.random.uniform(9000, 16000)
    elif tipo == "Minero":
        nivel_ingreso_promedio = np.random.uniform(6000, 10000)
    elif tipo == "Semiurbano":
        nivel_ingreso_promedio = np.random.uniform(5500, 9500)
    else:
        nivel_ingreso_promedio = np.random.uniform(3500, 6500)
    
    # Infraestructura
    if tipo in ["Industrial Pesado", "Urbano"]:
        cobertura_transporte_publico = np.random.uniform(65, 90)
        vehiculos_particulares_pct = np.random.uniform(45, 75)
    elif tipo == "Semiurbano":
        cobertura_transporte_publico = np.random.uniform(40, 70)
        vehiculos_particulares_pct = np.random.uniform(30, 50)
    else:
        cobertura_transporte_publico = np.random.uniform(15, 45)
        vehiculos_particulares_pct = np.random.uniform(12, 35)
    
    # Asignación de perfil predominante (más realista)
    if tipo == "Industrial Pesado":
        # Zonas industriales: población trabajadora, consciente del problema ambiental
        perfiles_posibles = ["El principiante", "La familia consciente", "El ecologista comprometido"]
        pesos = [0.50, 0.35, 0.15]
    elif tipo == "Urbano":
        perfiles_posibles = ["El principiante", "El ecologista comprometido", "La familia consciente"]
        pesos = [0.40, 0.35, 0.25]
    elif tipo == "Minero":
        perfiles_posibles = ["El principiante", "La familia consciente"]
        pesos = [0.55, 0.45]
    elif tipo == "Semiurbano":
        perfiles_posibles = ["El principiante", "La familia consciente"]
        pesos = [0.50, 0.50]
    else:  # Rural
        perfiles_posibles = ["La familia consciente", "El principiante"]
        pesos = [0.55, 0.45]
    
    perfil_predominante = random.choices(perfiles_posibles, weights=pesos)[0]
    
    # Nivel de contaminación cualitativo
    if emision_per_capita > 8000:
        nivel_contaminacion = "Muy Alto"
    elif emision_per_capita > 5000:
        nivel_contaminacion = "Alto"
    elif emision_per_capita > 3000:
        nivel_contaminacion = "Medio"
    elif emision_per_capita > 1500:
        nivel_contaminacion = "Bajo"
    else:
        nivel_contaminacion = "Muy Bajo"
    
    return {
        "municipio": municipio,
        "tipo_municipio": tipo,
        "caracteristica_especial": tipo_industria if tipo_industria else "ninguna",
        "poblacion": poblacion,
        "densidad_poblacional": densidad_poblacional,
        "emision_transporte_ton": round(emision_transporte, 2),
        "emision_energia_ton": round(emision_energia, 2),
        "emision_residuos_ton": round(emision_residuos, 2),
        "emision_industria_ton": round(emision_industria, 2),
        "emision_agricultura_ton": round(emision_agricultura, 2),
        "emision_total_ton": round(emision_total, 2),
        "emision_per_capita_kg": round(emision_per_capita, 2),
        "nivel_contaminacion": nivel_contaminacion,
        "nivel_ingreso_promedio_mxn": round(nivel_ingreso_promedio, 2),
        "cobertura_transporte_publico_pct": round(cobertura_transporte_publico, 2),
        "vehiculos_particulares_pct": round(vehiculos_particulares_pct, 2),
        "perfil_predominante": perfil_predominante,
        "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d")
    }

# Generar dataset completo
print("="*80)
print("GENERANDO DATASET SINTÉTICO REALISTA DE HUELLA DE CARBONO")
print("Basado en datos reales de contaminación en Hidalgo")
print("="*80)
print("\nFuentes consideradas:")
print("• Refinería Miguel Hidalgo (Tula): 136,000 ton SO2/año")
print("• Corredor Industrial Tula-Tepeji: 20% de contaminación CDMX")
print("• Parque Industrial Tizayuca: 88 empresas")
print("• Zonas mineras: Zimapán, Mineral del Monte, etc.")
print("• Presas contaminadas: Endhó, Requena")
print("\n" + "="*80 + "\n")

datos = [generar_datos_municipio(municipio) for municipio in municipios_hidalgo]

# Crear DataFrame
df = pd.DataFrame(datos)

# Ordenar por emisión per cápita (descendente)
df_ordenado = df.sort_values('emision_per_capita_kg', ascending=False)

# Guardar en CSV
archivo_csv = "huella_carbono_hidalgo_realista.csv"
df_ordenado.to_csv(archivo_csv, index=False, encoding='utf-8-sig')
print(f"✓ Dataset guardado como '{archivo_csv}'")

# Guardar también en Excel
archivo_excel = "huella_carbono_hidalgo_realista.xlsx"
df_ordenado.to_excel(archivo_excel, index=False, engine='openpyxl')
print(f"✓ Dataset guardado como '{archivo_excel}'")

# Mostrar estadísticas
print("\n" + "="*80)
print("RESUMEN DEL DATASET")
print("="*80)
print(f"Total de municipios: {len(df)}")
print(f"\nDistribución por tipo:")
print(df['tipo_municipio'].value_counts())
print(f"\nDistribución por perfil predominante:")
print(df['perfil_predominante'].value_counts())
print(f"\nNivel de contaminación:")
print(df['nivel_contaminacion'].value_counts())

print("\n" + "="*80)
print("TOP 10 MUNICIPIOS MÁS CONTAMINANTES (per cápita)")
print("="*80)
top10 = df_ordenado[['municipio', 'tipo_municipio', 'emision_per_capita_kg', 
                      'emision_total_ton', 'nivel_contaminacion']].head(10)
print(top10.to_string(index=False))

print("\n" + "="*80)
print("COMPARATIVA ZONA INDUSTRIAL vs RURAL")
print("="*80)
industriales = df[df['tipo_municipio'] == 'Industrial Pesado']['emision_per_capita_kg'].mean()
rurales = df[df['tipo_municipio'] == 'Rural']['emision_per_capita_kg'].mean()
print(f"Emisión promedio per cápita Industrial Pesado: {industriales:.2f} kg CO2e")
print(f"Emisión promedio per cápita Rural: {rurales:.2f} kg CO2e")
print(f"Diferencia: {((industriales/rurales - 1) * 100):.1f}% más en zonas industriales")

print("\n✓ Dataset generado exitosamente con datos realistas!")
print(f"Archivos creados: {archivo_csv} y {archivo_excel}")
print("="*80)