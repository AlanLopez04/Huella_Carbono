"""
Sistema de Cálculo de Huella de Carbono Personal
Implementación con Programación Orientada a Objetos y Funcional
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
from functools import reduce, partial
import json


@dataclass
class Actividad:
    """
    Unidad atómica que describe una acción o consumo.
    Ejemplo: 120 km en auto, 200 kWh/mes, 3 horas/día de uso de ordenador
    """
    categoria: str  # "transporte", "energia", "residuos", "tecnologia"
    sub_categoria: str  # "auto_gasolina", "electricidad", "laptop"
    cantidad: float  # Valor numérico
    unidad: str  # "km", "kWh", "horas"
    periodo: str  # "diario", "semanal", "mensual", "anual"
    factor_emision: Optional[float] = None  # kg CO₂e por unidad
    
    def calcular_emision(self, factores_repo: 'FactoresEmision') -> float:
        """
        Calcula la emisión de CO₂e para esta actividad.
        Si no tiene factor propio, consulta el repositorio.
        
        Returns:
            float: Emisión en kg CO₂e
        """
        if self.cantidad <= 0:
            return 0.0
        
        factor = self.factor_emision or factores_repo.obtener_factor(
            self.categoria, 
            self.sub_categoria
        )
        
        if factor is None:
            raise ValueError(f"No se encontró factor de emisión para {self.categoria}/{self.sub_categoria}")
        
        # Calcular emisión base
        emision_base = self.cantidad * factor
        
        # Normalizar a anual según periodo
        multiplicador_anual = {
            "diario": 365,
            "semanal": 52,
            "mensual": 12,
            "anual": 1
        }
        
        return emision_base * multiplicador_anual.get(self.periodo, 1)
    
    def es_valida(self) -> bool:
        """Verifica si la actividad tiene datos válidos"""
        return (
            self.cantidad > 0 and
            self.categoria and
            self.sub_categoria and
            self.unidad and
            self.periodo in ["diario", "semanal", "mensual", "anual"]
        )


class FactoresEmision:
    """
    Repositorio centralizado de factores de emisión.
    Única fuente autorizada para mantener coherencia.
    """
    
    def __init__(self):
        self.factores: Dict[str, Dict[str, float]] = self._cargar_factores_default()
    
    def _cargar_factores_default(self) -> Dict[str, Dict[str, float]]:
        """
        Carga factores de emisión por defecto (kg CO₂e por unidad).
        Basados en datos del IPCC y estudios de ciclo de vida.
        """
        return {
            "transporte": {
                "auto_gasolina": 0.192,  # kg CO₂e por km
                "auto_diesel": 0.171,
                "auto_electrico": 0.053,
                "autobus": 0.089,
                "metro": 0.041,
                "bicicleta": 0.0,
                "caminar": 0.0,
                "motocicleta": 0.113,
                "avion_corto": 0.255,  # < 1500 km
                "avion_largo": 0.195,  # > 1500 km
            },
            "energia": {
                "electricidad_red": 0.527,  # kg CO₂e por kWh (México)
                "electricidad_renovable": 0.041,
                "gas_natural": 0.202,  # por kWh térmico
                "gas_lp": 0.227,
                "carbon": 0.340,
            },
            "tecnologia": {
                "laptop": 0.020,  # kg CO₂e por hora de uso
                "desktop": 0.050,
                "smartphone": 0.005,
                "tablet": 0.012,
                "television": 0.030,
                "aire_acondicionado": 0.100,
                "refrigerador": 0.015,  # por hora de funcionamiento
                "lavadora": 0.600,  # por ciclo
            },
            "alimentacion": {
                "carne_res": 27.0,  # kg CO₂e por kg de alimento
                "carne_cerdo": 12.1,
                "carne_pollo": 6.9,
                "pescado": 5.5,
                "lacteos": 13.3,  # por litro de leche
                "huevos": 4.8,  # por docena
                "vegetales": 2.0,  # por kg
                "frutas": 1.1,
                "cereales": 2.5,
            },
            "residuos": {
                "residuos_organicos": 0.5,  # kg CO₂e por kg de residuo
                "residuos_inorganicos": 0.3,
                "plastico": 6.0,
                "papel_carton": 3.3,
                "vidrio": 0.8,
                "metal": 2.5,
            }
        }
    
    def obtener_factor(self, categoria: str, sub_categoria: str) -> Optional[float]:
        """Obtiene el factor de emisión para una categoría específica"""
        return self.factores.get(categoria, {}).get(sub_categoria)
    
    def actualizar_factor(self, categoria: str, sub_categoria: str, valor: float):
        """Actualiza o agrega un nuevo factor de emisión"""
        if categoria not in self.factores:
            self.factores[categoria] = {}
        self.factores[categoria][sub_categoria] = valor
    
    def cargar_desde_json(self, ruta_archivo: str):
        """Carga factores desde un archivo JSON externo"""
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                self.factores = json.load(f)
        except FileNotFoundError:
            print(f"Archivo {ruta_archivo} no encontrado. Usando factores por defecto.")
    
    def guardar_a_json(self, ruta_archivo: str):
        """Guarda los factores actuales a un archivo JSON"""
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(self.factores, f, indent=2, ensure_ascii=False)
    
    def obtener_todas_categorias(self) -> List[str]:
        """Retorna lista de todas las categorías disponibles"""
        return list(self.factores.keys())
    
    def obtener_subcategorias(self, categoria: str) -> List[str]:
        """Retorna lista de subcategorías para una categoría dada"""
        return list(self.factores.get(categoria, {}).keys())


class Usuario:
    """
    Representa al individuo que ingresa sus hábitos.
    Almacena una colección de Actividad.
    """
    
    def __init__(self, nombre: str, municipio: str, perfil: str):
        self.nombre = nombre
        self.municipio = municipio
        self.perfil = perfil  # "El principiante", "El ecologista comprometido", "La familia consciente"
        self.actividades: List[Actividad] = []
        self.fecha_registro = datetime.now()
    
    def agregar_actividad(self, actividad: Actividad):
        """Agrega una nueva actividad al usuario"""
        if actividad.es_valida():
            self.actividades.append(actividad)
        else:
            raise ValueError("La actividad no es válida")
    
    def quitar_actividad(self, indice: int):
        """Elimina una actividad por su índice"""
        if 0 <= indice < len(self.actividades):
            self.actividades.pop(indice)
    
    def obtener_actividades_por_categoria(self, categoria: str) -> List[Actividad]:
        """Filtra actividades por categoría usando filter()"""
        return list(filter(lambda act: act.categoria == categoria, self.actividades))
    
    def limpiar_actividades(self):
        """Elimina todas las actividades"""
        self.actividades = []
    
    def to_dict(self) -> Dict:
        """Convierte el usuario a diccionario para serialización"""
        return {
            "nombre": self.nombre,
            "municipio": self.municipio,
            "perfil": self.perfil,
            "fecha_registro": self.fecha_registro.isoformat(),
            "num_actividades": len(self.actividades)
        }


class CalculadoraCarbono:
    """
    Lógica central de cálculo.
    Usa FactoresEmision para convertir cada Actividad a toneladas de CO₂e.
    """
    
    def __init__(self, factores_emision: FactoresEmision):
        self.factores = factores_emision
    
    def calcular_por_actividad(self, actividad: Actividad) -> float:
        """
        Calcula emisión de una actividad individual.
        Retorna kg CO₂e por año.
        """
        return actividad.calcular_emision(self.factores)
    
    def calcular_total(self, actividades: List[Actividad]) -> float:
        """
        Calcula emisión total usando programación funcional.
        Usa map() para calcular cada actividad y reduce() para sumar.
        
        Returns:
            float: Total en toneladas CO₂e por año
        """
        # Filtrar actividades válidas
        actividades_validas = list(filter(lambda act: act.es_valida(), actividades))
        
        if not actividades_validas:
            return 0.0
        
        # Crear función parcial para calcular con los factores actuales
        calcular_con_factores = partial(self.calcular_por_actividad)
        
        # Aplicar cálculo a cada actividad usando map()
        emisiones_kg = list(map(calcular_con_factores, actividades_validas))
        
        # Sumar todas las emisiones usando reduce()
        total_kg = reduce(lambda x, y: x + y, emisiones_kg, 0.0)
        
        # Convertir a toneladas
        return total_kg / 1000.0
    
    def calcular_por_categoria(self, actividades: List[Actividad]) -> Dict[str, float]:
        """
        Agrupa y calcula emisiones por categoría.
        
        Returns:
            Dict: {categoria: toneladas_co2e}
        """
        categorias = {}
        
        for actividad in filter(lambda act: act.es_valida(), actividades):
            categoria = actividad.categoria
            emision = self.calcular_por_actividad(actividad) / 1000.0  # Convertir a toneladas
            
            if categoria in categorias:
                categorias[categoria] += emision
            else:
                categorias[categoria] = emision
        
        return categorias
    
    def generar_sugerencias(self, actividades: List[Actividad], 
                          perfil: str, top_n: int = 5) -> List['Sugerencia']:
        """
        Identifica actividades de mayor impacto y genera sugerencias.
        
        Args:
            actividades: Lista de actividades del usuario
            perfil: Perfil del usuario
            top_n: Número de sugerencias a generar
            
        Returns:
            List[Sugerencia]: Lista de recomendaciones
        """
        # Calcular emisión de cada actividad
        actividades_con_emision = [
            (act, self.calcular_por_actividad(act))
            for act in filter(lambda act: act.es_valida(), actividades)
        ]
        
        # Ordenar por emisión descendente
        actividades_ordenadas = sorted(
            actividades_con_emision, 
            key=lambda x: x[1], 
            reverse=True
        )
        
        sugerencias = []
        
        for actividad, emision_kg in actividades_ordenadas[:top_n]:
            sugerencia = self._crear_sugerencia_para_actividad(
                actividad, emision_kg, perfil
            )
            if sugerencia:
                sugerencias.append(sugerencia)
        
        return sugerencias
    
    def _crear_sugerencia_para_actividad(self, actividad: Actividad, 
                                         emision_kg: float, perfil: str) -> Optional['Sugerencia']:
        """Crea una sugerencia específica para una actividad"""
        
        # Base de conocimiento de sugerencias
        sugerencias_db = {
            "transporte": {
                "auto_gasolina": {
                    "El principiante": "Intenta usar transporte público o bicicleta 2 días a la semana",
                    "El ecologista comprometido": "Considera cambiar a un vehículo eléctrico o implementar carpool",
                    "La familia consciente": "Organiza carpools con otras familias para reducir viajes"
                },
                "auto_diesel": {
                    "El principiante": "Mantén tu auto en buen estado para optimizar consumo",
                    "El ecologista comprometido": "Planifica rutas eficientes y considera vehículo híbrido",
                    "La familia consciente": "Combina múltiples actividades en un solo viaje"
                }
            },
            "energia": {
                "electricidad_red": {
                    "El principiante": "Cambia a focos LED y desconecta aparatos en stand-by",
                    "El ecologista comprometido": "Instala paneles solares y optimiza aislamiento térmico",
                    "La familia consciente": "Establece horarios familiares para apagar dispositivos"
                }
            },
            "tecnologia": {
                "laptop": {
                    "El principiante": "Activa modo de ahorro de energía",
                    "El ecologista comprometido": "Apaga completamente cuando no uses por >1 hora",
                    "La familia consciente": "Limita tiempo de pantalla familiar a 2 horas/día"
                }
            }
        }
        
        # Buscar sugerencia específica
        texto = sugerencias_db.get(actividad.categoria, {}).get(
            actividad.sub_categoria, {}
        ).get(perfil, f"Reduce el uso de {actividad.sub_categoria}")
        
        # Estimar ahorro (25% de reducción estimada)
        ahorro_estimado = emision_kg * 0.25 / 1000.0  # En toneladas
        
        return Sugerencia(
            actividad_relacionada=f"{actividad.categoria}/{actividad.sub_categoria}",
            texto=texto,
            ahorro_estimado_ton=ahorro_estimado,
            dificultad="baja" if perfil == "El principiante" else "media",
            categoria=actividad.categoria
        )


@dataclass
class Sugerencia:
    """
    Recomendación práctica para reducir emisiones.
    """
    actividad_relacionada: str  # "transporte/auto_gasolina"
    texto: str  # "Usa bicicleta 3 días/semana"
    ahorro_estimado_ton: float  # Reducción en toneladas CO₂e/año
    dificultad: str  # "baja", "media", "alta"
    categoria: str  # Para agrupar sugerencias
    
    def to_dict(self) -> Dict:
        """Convierte la sugerencia a diccionario"""
        return {
            "actividad": self.actividad_relacionada,
            "recomendacion": self.texto,
            "ahorro_ton_co2e": round(self.ahorro_estimado_ton, 3),
            "dificultad": self.dificultad,
            "categoria": self.categoria
        }


class HuellaCarbono:
    """
    Objeto resultado que resume el cálculo de huella de carbono.
    """
    
    def __init__(self, total_ton_co2e: float, desglose: Dict[str, float], 
                 fecha: datetime, usuario: str):
        self.total_ton_co2e = total_ton_co2e
        self.desglose = desglose  # {categoria: toneladas}
        self.fecha = fecha
        self.usuario = usuario
    
    def generar_resumen(self) -> str:
        """Genera un resumen legible de la huella"""
        resumen = f"=== HUELLA DE CARBONO ==\n"
        resumen += f"Usuario: {self.usuario}\n"
        resumen += f"Fecha: {self.fecha.strftime('%Y-%m-%d %H:%M')}\n"
        resumen += f"Total: {self.total_ton_co2e:.3f} toneladas CO₂e/año\n\n"
        resumen += "Desglose por categoría:\n"
        
        for categoria, emision in sorted(self.desglose.items(), 
                                        key=lambda x: x[1], reverse=True):
            porcentaje = (emision / self.total_ton_co2e * 100) if self.total_ton_co2e > 0 else 0
            resumen += f"  • {categoria.capitalize()}: {emision:.3f} ton ({porcentaje:.1f}%)\n"
        
        return resumen
    
    def exportar_json(self) -> str:
        """Exporta la huella a formato JSON"""
        data = {
            "usuario": self.usuario,
            "fecha": self.fecha.isoformat(),
            "total_ton_co2e": round(self.total_ton_co2e, 3),
            "desglose": {k: round(v, 3) for k, v in self.desglose.items()},
            "equivalencias": self.calcular_equivalencias()
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def calcular_equivalencias(self) -> Dict[str, float]:
        """Calcula equivalencias comprensibles"""
        # 1 árbol absorbe ~20 kg CO₂/año
        arboles = self.total_ton_co2e * 1000 / 20
        
        # 1 coche promedio emite ~4.6 ton CO₂/año
        coches = self.total_ton_co2e / 4.6
        
        # 1 vuelo México-NY ~0.9 ton CO₂
        vuelos = self.total_ton_co2e / 0.9
        
        return {
            "arboles_necesarios": round(arboles, 1),
            "equivalente_coches": round(coches, 2),
            "equivalente_vuelos_mex_ny": round(vuelos, 1)
        }
    
    def comparar_con_promedio(self, promedio_nacional: float = 3.9) -> Dict[str, any]:
        """
        Compara con promedio nacional/regional.
        Promedio México: ~3.9 ton CO₂e per cápita
        """
        diferencia = self.total_ton_co2e - promedio_nacional
        porcentaje_diferencia = (diferencia / promedio_nacional * 100) if promedio_nacional > 0 else 0
        
        if diferencia > 0:
            estado = "por encima"
        elif diferencia < 0:
            estado = "por debajo"
        else:
            estado = "igual al"
        
        return {
            "tu_huella": round(self.total_ton_co2e, 2),
            "promedio_nacional": promedio_nacional,
            "diferencia": round(diferencia, 2),
            "porcentaje_diferencia": round(porcentaje_diferencia, 1),
            "estado": estado
        }


# ===== EJEMPLO DE USO =====

def ejemplo_uso_completo():
    """Ejemplo completo del uso del sistema"""
    
    print("="*70)
    print("SISTEMA DE CÁLCULO DE HUELLA DE CARBONO")
    print("="*70)
    
    # 1. Inicializar repositorio de factores
    factores = FactoresEmision()
    print("\n✓ Factores de emisión cargados")
    print(f"  Categorías disponibles: {', '.join(factores.obtener_todas_categorias())}")
    
    # 2. Crear calculadora
    calculadora = CalculadoraCarbono(factores)
    print("\n✓ Calculadora inicializada")
    
    # 3. Crear usuario
    usuario = Usuario(
        nombre="Juan Pérez",
        municipio="Pachuca de Soto",
        perfil="El ecologista comprometido"
    )
    print(f"\n✓ Usuario creado: {usuario.nombre}")
    print(f"  Municipio: {usuario.municipio}")
    print(f"  Perfil: {usuario.perfil}")
    
    # 4. Agregar actividades
    print("\n📝 Agregando actividades...")
    
    actividades_ejemplo = [
        Actividad(
            categoria="transporte",
            sub_categoria="auto_gasolina",
            cantidad=30,  # km
            unidad="km",
            periodo="diario"
        ),
        Actividad(
            categoria="energia",
            sub_categoria="electricidad_red",
            cantidad=250,  # kWh
            unidad="kWh",
            periodo="mensual"
        ),
        Actividad(
            categoria="tecnologia",
            sub_categoria="laptop",
            cantidad=8,  # horas
            unidad="horas",
            periodo="diario"
        ),
        Actividad(
            categoria="tecnologia",
            sub_categoria="aire_acondicionado",
            cantidad=5,
            unidad="horas",
            periodo="diario"
        ),
        Actividad(
            categoria="alimentacion",
            sub_categoria="carne_res",
            cantidad=0.5,  # kg
            unidad="kg",
            periodo="semanal"
        )
    ]
    
    for act in actividades_ejemplo:
        usuario.agregar_actividad(act)
        print(f"  • {act.categoria}/{act.sub_categoria}: {act.cantidad} {act.unidad}/{act.periodo}")
    
    # 5. Calcular huella total
    print("\n🧮 Calculando huella de carbono...")
    total_ton = calculadora.calcular_total(usuario.actividades)
    print(f"\n📊 HUELLA TOTAL: {total_ton:.3f} toneladas CO₂e/año")
    
    # 6. Calcular por categoría
    print("\n📈 Desglose por categoría:")
    desglose = calculadora.calcular_por_categoria(usuario.actividades)
    for categoria, emision in sorted(desglose.items(), key=lambda x: x[1], reverse=True):
        porcentaje = (emision / total_ton * 100) if total_ton > 0 else 0
        print(f"  • {categoria.capitalize()}: {emision:.3f} ton ({porcentaje:.1f}%)")
    
    # 7. Crear objeto HuellaCarbono
    huella = HuellaCarbono(
        total_ton_co2e=total_ton,
        desglose=desglose,
        fecha=datetime.now(),
        usuario=usuario.nombre
    )
    
    # 8. Mostrar equivalencias
    print("\n🌍 Equivalencias:")
    equiv = huella.calcular_equivalencias()
    print(f"  • Necesitarías {equiv['arboles_necesarios']:.0f} árboles para compensar")
    print(f"  • Equivale a {equiv['equivalente_coches']:.2f} coches por un año")
    print(f"  • Equivale a {equiv['equivalente_vuelos_mex_ny']:.1f} vuelos México-NY")
    
    # 9. Comparar con promedio nacional
    print("\n📊 Comparación con promedio nacional (México: 3.9 ton):")
    comparacion = huella.comparar_con_promedio()
    print(f"  • Tu huella: {comparacion['tu_huella']} ton")
    print(f"  • Promedio: {comparacion['promedio_nacional']} ton")
    print(f"  • Diferencia: {comparacion['diferencia']} ton ({comparacion['porcentaje_diferencia']}%)")
    print(f"  • Estás {comparacion['estado']} promedio")
    
    # 10. Generar sugerencias
    print("\n💡 Generando sugerencias personalizadas...")
    sugerencias = calculadora.generar_sugerencias(
        usuario.actividades,
        usuario.perfil,
        top_n=5
    )
    
    print(f"\n🎯 Top {len(sugerencias)} recomendaciones:")
    for i, sug in enumerate(sugerencias, 1):
        print(f"\n{i}. [{sug.categoria.upper()}] {sug.texto}")
        print(f"   Ahorro estimado: {sug.ahorro_estimado_ton:.3f} ton CO₂e/año")
        print(f"   Dificultad: {sug.dificultad}")
    
    # 11. Exportar resultados
    print("\n💾 Exportando resultados...")
    print("\n" + "="*70)
    print(huella.generar_resumen())
    print("="*70)
    
    # Exportar a JSON
    json_output = huella.exportar_json()
    with open('huella_carbono_resultado.json', 'w', encoding='utf-8') as f:
        f.write(json_output)
    print("\n✓ Resultados guardados en 'huella_carbono_resultado.json'")
    
    print("\n" + "="*70)
    print("PROCESO COMPLETADO")
    print("="*70)


def ejemplo_programacion_funcional():
    """Ejemplo enfocado en uso de map, filter, reduce"""
    
    print("\n" + "="*70)
    print("DEMOSTRACIÓN DE PROGRAMACIÓN FUNCIONAL")
    print("="*70)
    
    factores = FactoresEmision()
    calculadora = CalculadoraCarbono(factores)
    
    # Crear actividades de prueba
    actividades = [
        Actividad("transporte", "auto_gasolina", 50, "km", "diario"),
        Actividad("transporte", "bicicleta", 10, "km", "diario"),
        Actividad("energia", "electricidad_red", 300, "kWh", "mensual"),
        Actividad("tecnologia", "laptop", 0, "horas", "diario"),  # Inválida (cantidad = 0)
        Actividad("alimentacion", "carne_res", 1, "kg", "semanal"),
    ]
    
    print("\n1️⃣ FILTER: Filtrar actividades válidas")
    print("-" * 70)
    actividades_validas = list(filter(lambda act: act.es_valida(), actividades))
    print(f"Actividades totales: {len(actividades)}")
    print(f"Actividades válidas: {len(actividades_validas)}")
    for act in actividades_validas:
        print(f"  ✓ {act.categoria}/{act.sub_categoria}")
    
    print("\n2️⃣ MAP: Calcular emisión de cada actividad")
    print("-" * 70)
    # Crear función parcial
    calcular_func = partial(calculadora.calcular_por_actividad)
    emisiones = list(map(calcular_func, actividades_validas))
    
    for act, emision in zip(actividades_validas, emisiones):
        print(f"  • {act.categoria}/{act.sub_categoria}: {emision:,.2f} kg CO₂e/año")
    
    print("\n3️⃣ REDUCE: Sumar todas las emisiones")
    print("-" * 70)
    total_kg = reduce(lambda x, y: x + y, emisiones, 0.0)
    total_ton = total_kg / 1000.0
    print(f"Total: {total_kg:,.2f} kg CO₂e/año")
    print(f"Total: {total_ton:.3f} toneladas CO₂e/año")
    
    print("\n4️⃣ Combinación: Filter + Map + Reduce en una sola operación")
    print("-" * 70)
    total_funcional = reduce(
        lambda acc, val: acc + val,
        map(
            calculadora.calcular_por_actividad,
            filter(lambda act: act.es_valida(), actividades)
        ),
        0.0
    ) / 1000.0
    
    print(f"Resultado con programación funcional: {total_funcional:.3f} ton")
    
    print("\n5️⃣ Filtrar por categoría usando filter")
    print("-" * 70)
    transporte = list(filter(
        lambda act: act.categoria == "transporte",
        actividades_validas
    ))
    print(f"Actividades de transporte: {len(transporte)}")
    for act in transporte:
        print(f"  • {act.sub_categoria}: {act.cantidad} {act.unidad}")
    
    print("\n" + "="*70)


# Ejecutar ejemplos si se corre el archivo directamente
if __name__ == "__main__":
    # Ejemplo completo
    ejemplo_uso_completo()
    
    # Ejemplo de programación funcional
    print("\n\n")
    ejemplo_programacion_funcional()