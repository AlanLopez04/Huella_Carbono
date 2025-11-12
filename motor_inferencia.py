"""
Motor de Inferencia Basado en Reglas de Producción
Sistema de Razonamiento hacia Adelante (Forward Chaining)

PARADIGMA LÓGICO:
- Utiliza reglas de producción: SI <condiciones> ENTONCES <conclusión>
- Implementa encadenamiento hacia adelante
- Aplica búsqueda sistemática sobre el espacio de hechos
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from firebase_config import FirebaseConnection
from functools import reduce


@dataclass
class Hecho:
    """
    Representa un hecho en la base de conocimientos.
    Los hechos son afirmaciones sobre el mundo que son verdaderas.
    
    PARADIGMA LÓGICO: Los hechos son proposiciones atómicas que
    el motor de inferencia evalúa contra las reglas.
    """
    tipo: str  # "actividad", "municipio", "perfil", "emision"
    atributo: str  # "categoria", "nivel_contaminacion", etc.
    valor: Any  # Valor del atributo
    confianza: float = 1.0  # Grado de certeza (0.0 a 1.0)
    
    def __str__(self):
        return f"{self.tipo}.{self.atributo} = {self.valor} (confianza: {self.confianza})"


class MemoriaTrabajo:
    """
    Memoria de Trabajo (Working Memory) del sistema de producción.
    Almacena los hechos conocidos durante la inferencia.
    
    REGLA DE NEGOCIO: La memoria de trabajo debe actualizarse
    dinámicamente conforme se infieren nuevos hechos.
    """
    
    def __init__(self):
        self.hechos: List[Hecho] = []
        self.historial_inferencias: List[Dict] = []
    
    def agregar_hecho(self, hecho: Hecho):
        """Agrega un hecho a la memoria de trabajo"""
        # Evitar duplicados exactos
        if not any(h.tipo == hecho.tipo and 
                  h.atributo == hecho.atributo and 
                  h.valor == hecho.valor 
                  for h in self.hechos):
            self.hechos.append(hecho)
    
    def obtener_hechos_por_tipo(self, tipo: str) -> List[Hecho]:
        """Filtra hechos por tipo usando filter() (Programación Funcional)"""
        return list(filter(lambda h: h.tipo == tipo, self.hechos))
    
    def obtener_valor(self, tipo: str, atributo: str) -> Optional[Any]:
        """Busca el valor de un atributo específico"""
        for hecho in self.hechos:
            if hecho.tipo == tipo and hecho.atributo == atributo:
                return hecho.valor
        return None
    
    def limpiar(self):
        """Limpia la memoria de trabajo"""
        self.hechos = []
        self.historial_inferencias = []
    
    def __str__(self):
        return f"Memoria de Trabajo: {len(self.hechos)} hechos"


class MotorInferencia:
    """
    Motor de Inferencia basado en Encadenamiento Hacia Adelante.
    
    ARQUITECTURA DEL SISTEMA DE PRODUCCIÓN:
    1. Cargar reglas desde Firebase
    2. Inicializar memoria de trabajo con hechos del usuario
    3. Ciclo de inferencia:
       a) Buscar reglas aplicables (MATCH)
       b) Seleccionar regla por prioridad (RESOLVE)
       c) Ejecutar acción de la regla (EXECUTE)
       d) Agregar nuevos hechos a la memoria
    4. Repetir hasta que no haya más reglas aplicables
    
    BÚSQUEDA SISTEMÁTICA:
    - Se evalúan todas las reglas en orden de prioridad
    - Se aplica la primera regla que satisface sus condiciones
    - Se continúa hasta alcanzar un punto fijo (no más reglas aplicables)
    """
    
    def __init__(self):
        self.firebase = FirebaseConnection()
        self.memoria_trabajo = MemoriaTrabajo()
        self.reglas = {}
        self.conclusiones = []
        # La carga de reglas siempre se llama al inicio
        self.cargar_reglas()
    
    def cargar_reglas(self):
        """Intenta cargar reglas desde Firebase. Si falla, usa el fallback."""
        print("\n🔄 Intentando cargar reglas desde Firebase...")
        
        try:
            # Llama a tu conexión real a Firebase
            reglas_reales = self.firebase.obtener_reglas()
        except Exception as e:
            # Capturamos cualquier error en la conexión/carga
            reglas_reales = None
            print(f"ERROR: Fallo al obtener reglas de Firebase: {e}")
        
        # -----------------------------------------------------------
        # LÓGICA DE SIMULACIÓN / FALLBACK:
        # -----------------------------------------------------------
        # Si no se obtuvieron reglas válidas (es None, no es un dict, o está vacío)
        if not reglas_reales or not isinstance(reglas_reales, dict) or len(reglas_reales) == 0:
            print("⚠️ No se pudieron cargar reglas reales válidas. Usando reglas por defecto (fallback).")
            self.reglas = self._reglas_fallback()
            total_reglas = sum(len(grupo) for grupo in self.reglas.values())
            print(f"DEBUG: {total_reglas} reglas fallback cargadas.")
        else:
            # Si se obtuvieron datos válidos (cargados exitosamente de Firebase)
            self.reglas = reglas_reales 
            total_reglas = sum(len(grupo) for grupo in self.reglas.values())
            print(f"✅ {total_reglas} reglas cargadas correctamente desde Firebase (real).")
    
    def _reglas_fallback(self) -> Dict:
        """Reglas mínimas SIMULADAS para garantizar el funcionamiento del motor."""
        return {
            "reglas_basicas": {
                "R_EMISION_ALTA": {
                    "nombre": "Alerta de Emisión Alta",
                    # Usa la emisión total en kg
                    "condiciones": {"emision_per_capita_mayor_que": 5000}, 
                    "conclusion": {"alerta": "Tu huella es significativamente alta. Es una prioridad identificar el foco."},
                    "prioridad": 10
                },
                "R_MUNICIPIO_INDUSTRIAL": {
                    "nombre": "Alerta de Contexto Municipal",
                    # Las condiciones se buscan por combinación de tipo_atributo (ej: municipio_tipo)
                    "condiciones": {"municipio_tipo": "Industrial Pesado", "municipio_nivel_contaminacion": "Muy Alto"},
                    "conclusion": {"contexto": "Tu municipio tiene altos factores de riesgo ambiental. Tu huella personal es crítica."},
                    "prioridad": 8
                },
                "R_BAJO_IMPACTO": {
                    "nombre": "Refuerzo Positivo",
                    "condiciones": {"emision_per_capita_menor_que": 3000, "usuario_perfil": "El ecologista comprometido"},
                    "conclusion": {"refuerzo_positivo": "¡Felicidades! Tu esfuerzo como ecologista comprometido está dando frutos."},
                    "prioridad": 5
                },
            },
            # Puedes agregar más grupos de reglas aquí si lo deseas
        }
    
    def inicializar_hechos_desde_usuario(self, datos_usuario: Dict):
        """
        Convierte los datos del usuario en hechos para la memoria de trabajo.
        
        Args:
            datos_usuario: Diccionario con datos del usuario y sus actividades
        
        PARADIGMA LÓGICO: Los datos de entrada se transforman en
        hechos (proposiciones) que el motor puede razonar.
        """
        print("\n📝 Inicializando hechos en memoria de trabajo...")
        
        # Hechos del municipio
        if 'municipio' in datos_usuario:
            self.memoria_trabajo.agregar_hecho(
                Hecho("municipio", "nombre", datos_usuario['municipio'])
            )
            self.memoria_trabajo.agregar_hecho(
                Hecho("municipio", "tipo", datos_usuario.get('tipo_municipio', 'Desconocido'))
            )
            self.memoria_trabajo.agregar_hecho(
                Hecho("municipio", "nivel_contaminacion", 
                      datos_usuario.get('nivel_contaminacion', 'Medio'))
            )
            self.memoria_trabajo.agregar_hecho(
                Hecho("municipio", "emision_industria", 
                      datos_usuario.get('emision_industria_ton', 0))
            )
        
        # Hechos del perfil
        if 'perfil' in datos_usuario:
            self.memoria_trabajo.agregar_hecho(
                Hecho("usuario", "perfil", datos_usuario['perfil'])
            )
        
        # Hechos de emisiones
        if 'emision_per_capita_kg' in datos_usuario:
            self.memoria_trabajo.agregar_hecho(
                Hecho("emision", "per_capita", datos_usuario['emision_per_capita_kg'])
            )
        
        # Hechos de actividades
        if 'actividades' in datos_usuario:
            for actividad in datos_usuario['actividades']:
                self.memoria_trabajo.agregar_hecho(
                    Hecho("actividad", "categoria", actividad.get('categoria'))
                )
                self.memoria_trabajo.agregar_hecho(
                    Hecho("actividad", "sub_categoria", actividad.get('sub_categoria'))
                )
                self.memoria_trabajo.agregar_hecho(
                    Hecho("actividad", "cantidad", actividad.get('cantidad'))
                )
        
        print(f"✅ {len(self.memoria_trabajo.hechos)} hechos inicializados")
    
    def evaluar_condicion(self, condicion: Dict, hechos: List[Hecho]) -> bool:
        """
        Evalúa si una condición se cumple dados los hechos actuales.
        
        BÚSQUEDA SISTEMÁTICA: Utiliza pattern matching para encontrar
        hechos que satisfagan las condiciones de la regla.
        
        Args:
            condicion: Diccionario con la condición a evaluar
            hechos: Lista de hechos en memoria de trabajo
        
        Returns:
            bool: True si la condición se cumple
        """
        # Operador lógico (AND por defecto)
        operador = condicion.get('operador', 'AND')
        
        # Buscar hechos relevantes usando filter() (Programación Funcional)
        hechos_relevantes = list(filter(
            lambda h: any(
                cond_key in h.atributo or 
                cond_key == h.atributo or
                (cond_key.startswith(h.tipo) and cond_key.endswith(h.atributo))
                for cond_key in condicion.keys() 
                if cond_key != 'operador'
            ),
            hechos
        ))
        
        resultados = []
        
        # Evaluar cada condición
        for clave, valor in condicion.items():
            if clave == 'operador':
                continue
            
            # Extraer tipo de comparación
            if clave.endswith('_mayor_que'):
                atributo_base = clave.replace('_mayor_que', '')
                valor_hecho = self._buscar_valor_hecho(atributo_base, hechos)
                if valor_hecho is not None:
                    resultados.append(valor_hecho > valor)
                else:
                    resultados.append(False)
            
            elif clave.endswith('_menor_que'):
                atributo_base = clave.replace('_menor_que', '')
                valor_hecho = self._buscar_valor_hecho(atributo_base, hechos)
                if valor_hecho is not None:
                    resultados.append(valor_hecho < valor)
                else:
                    resultados.append(False)
            
            else:
                # Comparación directa
                valor_hecho = self._buscar_valor_hecho(clave, hechos)
                if valor_hecho is not None:
                    resultados.append(valor_hecho == valor)
                else:
                    # Verificar alternativas (ej: nivel_contaminacion_alt)
                    if f"{clave}_alt" in condicion:
                        valor_alt = condicion[f"{clave}_alt"]
                        valor_hecho_alt = self._buscar_valor_hecho(clave, hechos)
                        if valor_hecho_alt is not None:
                            resultados.append(valor_hecho_alt == valor_alt)
                        else:
                            resultados.append(False)
                    else:
                        resultados.append(False)
        
        # Aplicar operador lógico usando reduce() (Programación Funcional)
        if operador == 'AND':
            return reduce(lambda x, y: x and y, resultados, True) if resultados else False
        elif operador == 'OR':
            return reduce(lambda x, y: x or y, resultados, False) if resultados else False
        else:
            return False
    
    def _buscar_valor_hecho(self, atributo: str, hechos: List[Hecho]) -> Optional[Any]:
        """Busca el valor de un atributo en la lista de hechos"""
        for hecho in hechos:
            if atributo in [hecho.atributo, f"{hecho.tipo}_{hecho.atributo}", 
                           hecho.atributo.replace('_', '')]:
                return hecho.valor
            # Casos especiales
            if atributo == "cantidad" and hecho.atributo == "cantidad":
                return hecho.valor
            if atributo == "emision_per_capita" and hecho.atributo == "per_capita":
                return hecho.valor
        return None
    
    def ejecutar_inferencia(self, max_iteraciones: int = 10) -> List[Dict]:
        """
        Ejecuta el ciclo de inferencia (MATCH-RESOLVE-EXECUTE).
        
        ENCADENAMIENTO HACIA ADELANTE:
        1. MATCH: Buscar todas las reglas cuyas condiciones se satisfacen
        2. RESOLVE: Seleccionar la regla de mayor prioridad
        3. EXECUTE: Aplicar la acción de la regla
        4. Repetir hasta que no haya más reglas aplicables o se alcance max_iteraciones
        
        Args:
            max_iteraciones: Límite de iteraciones para evitar loops infinitos
        
        Returns:
            List[Dict]: Lista de conclusiones inferidas
        """
        print("\n🧠 Iniciando proceso de inferencia...")
        print("="*70)
        
        iteracion = 0
        reglas_disparadas = set()
        
        while iteracion < max_iteraciones:
            iteracion += 1
            print(f"\n--- Iteración {iteracion} ---")
            
            # MATCH: Encontrar reglas aplicables
            reglas_aplicables = self._buscar_reglas_aplicables(reglas_disparadas)
            
            if not reglas_aplicables:
                print("✅ No hay más reglas aplicables. Inferencia completa.")
                break
            
            # RESOLVE: Seleccionar regla de mayor prioridad
            regla_seleccionada = max(reglas_aplicables, 
                                    key=lambda r: r['regla']['prioridad'])
            
            print(f"🎯 Regla seleccionada: {regla_seleccionada['regla']['nombre']} "
                  f"(Prioridad: {regla_seleccionada['regla']['prioridad']})")
            
            # EXECUTE: Aplicar la regla
            self._ejecutar_regla(regla_seleccionada)
            
            # Marcar regla como disparada
            reglas_disparadas.add(regla_seleccionada['id'])
        
        print("\n" + "="*70)
        print(f"✅ Inferencia completada en {iteracion} iteraciones")
        print(f"📊 Total de conclusiones: {len(self.conclusiones)}")
        
        # Guardar inferencias en Firebase
        if self.conclusiones:
            self.firebase.guardar_inferencia(
                usuario=self.memoria_trabajo.obtener_valor("usuario", "nombre") or "Anónimo",
                conclusion=self.conclusiones
            )
        
        return self.conclusiones
    
    def _buscar_reglas_aplicables(self, reglas_disparadas: set) -> List[Dict]:
        """
        Busca todas las reglas cuyas condiciones se cumplen.
        
        BÚSQUEDA SISTEMÁTICA: Evalúa cada regla contra los hechos actuales.
        """
        reglas_aplicables = []
        
        for grupo_nombre, grupo_reglas in self.reglas.items():
            for regla_id, regla in grupo_reglas.items():
                # Saltar reglas ya disparadas
                if regla_id in reglas_disparadas:
                    continue
                
                # Evaluar condiciones
                if self.evaluar_condicion(regla['condiciones'], 
                                         self.memoria_trabajo.hechos):
                    reglas_aplicables.append({
                        'id': regla_id,
                        'grupo': grupo_nombre,
                        'regla': regla
                    })
        
        return reglas_aplicables
    
    def _ejecutar_regla(self, regla_info: Dict):
        """
        Ejecuta la acción de una regla y agrega nuevos hechos.
        
        REGLA DE NEGOCIO: La conclusión de una regla puede generar
        nuevos hechos que disparen otras reglas (encadenamiento).
        """
        regla = regla_info['regla']
        conclusion = regla['conclusion']
        
        # Agregar conclusión a la lista
        self.conclusiones.append({
            'regla': regla['nombre'],
            'conclusion': conclusion,
            'prioridad': regla['prioridad']
        })
        
        print(f"  ✓ Conclusión: {conclusion}")
        
        # Generar nuevos hechos derivados (si aplica)
        if 'sugerencia' in conclusion:
            self.memoria_trabajo.agregar_hecho(
                Hecho("inferencia", "sugerencia", conclusion['sugerencia'])
            )
        
        if 'alerta' in conclusion:
            self.memoria_trabajo.agregar_hecho(
                Hecho("inferencia", "alerta", conclusion['alerta'])
            )
    
    def obtener_sugerencias_formateadas(self) -> List[str]:
        """
        Formatea las conclusiones como sugerencias legibles.
        
        Returns:
            List[str]: Lista de sugerencias en formato texto
        """
        sugerencias = []
        
        for conclusion in self.conclusiones:
            contenido = conclusion['conclusion']
            
            if 'sugerencia' in contenido:
                sugerencias.append(f"💡 {contenido['sugerencia']}")
            
            if 'alerta' in contenido:
                sugerencias.append(f"⚠️ {contenido['alerta']}")
            
            if 'refuerzo_positivo' in contenido:
                sugerencias.append(f"🌟 {contenido['refuerzo_positivo']}")
            
            if 'contexto' in contenido:
                sugerencias.append(f"📍 {contenido['contexto']}")
        
        return sugerencias
    
    def reiniciar(self):
        """Reinicia el motor para un nuevo análisis"""
        self.memoria_trabajo.limpiar()
        self.conclusiones = []


# ===== EJEMPLO DE USO =====

def ejemplo_inferencia():
    """Ejemplo de uso del motor de inferencia"""
    
    print("="*70)
    print("DEMOSTRACIÓN DEL MOTOR DE INFERENCIA")
    print("="*70)
    
    # Crear motor
    motor = MotorInferencia()
    
    # Datos de ejemplo de un usuario
    datos_usuario = {
        'municipio': 'Tula de Allende',
        'tipo_municipio': 'Industrial Pesado',
        'nivel_contaminacion': 'Muy Alto',
        'emision_industria_ton': 180000,
        'perfil': 'El ecologista comprometido',
        'emision_per_capita_kg': 8500,
        'actividades': [
            {'categoria': 'transporte', 'sub_categoria': 'auto_gasolina', 'cantidad': 50},
            {'categoria': 'energia', 'sub_categoria': 'electricidad_red', 'cantidad': 350}
        ]
    }
    
    # Inicializar hechos
    motor.inicializar_hechos_desde_usuario(datos_usuario)
    
    # Ejecutar inferencia
    conclusiones = motor.ejecutar_inferencia()
    
    # Mostrar resultados
    print("\n" + "="*70)
    print("RESULTADOS DE LA INFERENCIA")
    print("="*70)
    
    sugerencias = motor.obtener_sugerencias_formateadas()
    for i, sug in enumerate(sugerencias, 1):
        print(f"{i}. {sug}")


if __name__ == "__main__":
    ejemplo_inferencia()