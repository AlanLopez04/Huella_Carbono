"""
Configuración de Firebase para Base de Conocimientos
Conexión a Realtime Database para almacenar reglas y hechos
"""

import firebase_admin
from firebase_admin import credentials, db
import json
import os

class FirebaseConnection:
    """
    Clase para manejar la conexión con Firebase Realtime Database.
    Implementa el patrón Singleton para garantizar una única instancia.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseConnection, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.db_ref = None
        self.inicializar_firebase()
    
    def inicializar_firebase(self):
        """
        Inicializa la conexión con Firebase usando credenciales.
        
        REGLA DE NEGOCIO: El sistema debe conectarse a Firebase al inicio
        para garantizar disponibilidad de la base de conocimientos.
        """
        try:
            # Ruta al archivo de credenciales
            # IMPORTANTE: Descarga tu archivo JSON desde Firebase Console
            cred_path = "firebase-credentials.json"
            
            if not os.path.exists(cred_path):
                print("⚠️ Advertencia: No se encontró archivo de credenciales de Firebase")
                print("Por favor descarga 'firebase-credentials.json' desde Firebase Console")
                return
            
            # Inicializar app de Firebase
            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://calculadora-carbono-hidalgo-default-rtdb.firebaseio.com/'  # Cambia esto por tu URL
                })
            
            # Referencia a la base de datos
            self.db_ref = db.reference('/')
            print("✅ Conexión a Firebase establecida correctamente")
            
        except Exception as e:
            print(f"❌ Error al conectar con Firebase: {e}")
            self.db_ref = None
    
    def guardar_reglas(self, reglas_dict):
        """
        Guarda las reglas de producción en Firebase.
        
        Args:
            reglas_dict: Diccionario con las reglas del sistema
        
        REGLA DE NEGOCIO: Las reglas deben persistirse para ser
        reutilizables entre sesiones y actualizables en tiempo real.
        """
        if self.db_ref is None:
            print("⚠️ No hay conexión a Firebase")
            return False
        
        try:
            self.db_ref.child('reglas_produccion').set(reglas_dict)
            print("✅ Reglas guardadas en Firebase")
            return True
        except Exception as e:
            print(f"❌ Error al guardar reglas: {e}")
            return False
    
    def obtener_reglas(self):
        """
        Recupera las reglas de producción desde Firebase.
        
        Returns:
            dict: Diccionario con las reglas o None si hay error
        
        REGLA DE NEGOCIO: El motor de inferencia debe consultar
        las reglas más recientes antes de cada ejecución.
        """
        if self.db_ref is None:
            print("⚠️ No hay conexión a Firebase")
            return None
        
        try:
            reglas = self.db_ref.child('reglas_produccion').get()
            return reglas
        except Exception as e:
            print(f"❌ Error al obtener reglas: {e}")
            return None
    
    def guardar_hecho(self, tipo_hecho, datos):
        """
        Guarda un hecho (dato del usuario) en Firebase.
        
        Args:
            tipo_hecho: Categoría del hecho (ej: "actividad", "perfil")
            datos: Diccionario con los datos del hecho
        
        REGLA DE NEGOCIO: Los hechos deben almacenarse para
        análisis histórico y mejora del sistema de inferencia.
        """
        if self.db_ref is None:
            return False
        
        try:
            from datetime import datetime
            timestamp = datetime.now().isoformat()
            
            self.db_ref.child('hechos').child(tipo_hecho).push({
                'datos': datos,
                'timestamp': timestamp
            })
            return True
        except Exception as e:
            print(f"❌ Error al guardar hecho: {e}")
            return False
    
    def guardar_inferencia(self, usuario, conclusion):
        """
        Guarda el resultado de una inferencia (conclusión del motor).
        
        REGLA DE NEGOCIO: Las inferencias exitosas deben registrarse
        para validar la efectividad del sistema de reglas.
        """
        if self.db_ref is None:
            return False
        
        try:
            from datetime import datetime
            self.db_ref.child('inferencias').push({
                'usuario': usuario,
                'conclusion': conclusion,
                'timestamp': datetime.now().isoformat()
            })
            return True
        except Exception as e:
            print(f"❌ Error al guardar inferencia: {e}")
            return False


def inicializar_reglas_default():
    """
    Inicializa las reglas de producción por defecto en Firebase.
    Esta función se ejecuta una sola vez para poblar la base de conocimientos.
    
    REGLAS DE NEGOCIO:
    - Cada regla debe tener: condiciones, acción y prioridad
    - Las condiciones se evalúan con operadores lógicos (AND, OR)
    - La prioridad determina el orden de evaluación (mayor = más prioritaria)
    """
    
    reglas = {
        "reglas_transporte": {
            "R1": {
                "nombre": "Transporte Alto Gasolina",
                "condiciones": {
                    "categoria": "transporte",
                    "sub_categoria": "auto_gasolina",
                    "cantidad_mayor_que": 30,  # km/día
                    "operador": "AND"
                },
                "conclusion": {
                    "sugerencia": "Reducir uso de vehículo particular",
                    "alternativas": ["transporte_publico", "bicicleta", "carpooling"],
                    "ahorro_estimado_pct": 40
                },
                "prioridad": 10
            },
            "R2": {
                "nombre": "Uso Bicicleta Positivo",
                "condiciones": {
                    "categoria": "transporte",
                    "sub_categoria": "bicicleta",
                    "cantidad_mayor_que": 5,  # km/día
                    "operador": "AND"
                },
                "conclusion": {
                    "refuerzo_positivo": "Excelente uso de transporte sostenible",
                    "medalla": "eco_ciclista",
                    "ahorro_real_kg": 150  # kg CO2e/mes
                },
                "prioridad": 8
            }
        },
        
        "reglas_energia": {
            "R3": {
                "nombre": "Consumo Eléctrico Alto",
                "condiciones": {
                    "categoria": "energia",
                    "sub_categoria": "electricidad_red",
                    "cantidad_mayor_que": 300,  # kWh/mes
                    "operador": "AND"
                },
                "conclusion": {
                    "sugerencia": "Optimizar consumo eléctrico",
                    "acciones": ["cambiar_focos_led", "desconectar_standby", "paneles_solares"],
                    "ahorro_estimado_pct": 25
                },
                "prioridad": 9
            },
            "R4": {
                "nombre": "Uso Energía Renovable",
                "condiciones": {
                    "categoria": "energia",
                    "sub_categoria": "electricidad_renovable",
                    "cantidad_mayor_que": 0,
                    "operador": "AND"
                },
                "conclusion": {
                    "refuerzo_positivo": "Compromiso con energías limpias",
                    "medalla": "energia_verde",
                    "ahorro_real_kg": 200
                },
                "prioridad": 7
            }
        },
        
        "reglas_municipio": {
            "R5": {
                "nombre": "Municipio Alta Contaminación",
                "condiciones": {
                    "nivel_contaminacion": "Muy Alto",
                    "operador": "OR",
                    "nivel_contaminacion_alt": "Alto"
                },
                "conclusion": {
                    "alerta": "Tu municipio tiene alta contaminación",
                    "acciones_comunitarias": [
                        "participar_reforestacion",
                        "promover_transporte_limpio",
                        "exigir_industrias_limpias"
                    ],
                    "impacto_multiplicador": 3  # Cada acción tiene 3x impacto
                },
                "prioridad": 10
            },
            "R6": {
                "nombre": "Municipio Industrial",
                "condiciones": {
                    "tipo_municipio": "Industrial Pesado",
                    "operador": "AND",
                    "emision_industria_mayor_que": 50000  # toneladas
                },
                "conclusion": {
                    "contexto": "Zona con alta actividad industrial",
                    "sugerencia": "Acciones individuales son más críticas aquí",
                    "enfoque": "compensacion_comunitaria"
                },
                "prioridad": 9
            }
        },
        
        "reglas_perfil": {
            "R7": {
                "nombre": "Perfil Principiante",
                "condiciones": {
                    "perfil": "El principiante",
                    "operador": "AND"
                },
                "conclusion": {
                    "estilo_sugerencias": "simple_visual",
                    "complejidad": "baja",
                    "frecuencia_recordatorios": "alta"
                },
                "prioridad": 5
            },
            "R8": {
                "nombre": "Perfil Ecologista Comprometido",
                "condiciones": {
                    "perfil": "El ecologista comprometido",
                    "operador": "AND"
                },
                "conclusion": {
                    "estilo_sugerencias": "detallado_tecnico",
                    "complejidad": "alta",
                    "incluir_datos_avanzados": True
                },
                "prioridad": 5
            }
        },
        
        "reglas_combinadas": {
            "R9": {
                "nombre": "Alta Emisión + Municipio Industrial",
                "condiciones": {
                    "emision_per_capita_mayor_que": 5000,  # kg CO2e
                    "operador": "AND",
                    "tipo_municipio": "Industrial Pesado"
                },
                "conclusion": {
                    "alerta_critica": "Huella muy alta en zona crítica",
                    "prioridad_accion": "urgente",
                    "sugerencias_personalizadas": [
                        "cambio_radical_transporte",
                        "auditoria_energetica_hogar",
                        "activismo_comunitario"
                    ]
                },
                "prioridad": 10
            },
            "R10": {
                "nombre": "Bajo Impacto + Rural",
                "condiciones": {
                    "emision_per_capita_menor_que": 2000,
                    "operador": "AND",
                    "tipo_municipio": "Rural"
                },
                "conclusion": {
                    "reconocimiento": "Huella de carbono ejemplar",
                    "medalla": "guardian_rural",
                    "compartir_buenas_practicas": True
                },
                "prioridad": 6
            }
        }
    }
    
    # Guardar en Firebase
    firebase_conn = FirebaseConnection()
    firebase_conn.guardar_reglas(reglas)
    
    print("✅ Reglas de producción inicializadas en Firebase")
    return reglas


# Ejecutar inicialización si se corre directamente
if __name__ == "__main__":
    print("="*70)
    print("INICIALIZACIÓN DE BASE DE CONOCIMIENTOS EN FIREBASE")
    print("="*70)
    
    inicializar_reglas_default()
    
    # Verificar conexión
    firebase_conn = FirebaseConnection()
    reglas = firebase_conn.obtener_reglas()
    
    if reglas:
        print(f"\n✅ Verificación exitosa: {len(reglas)} grupos de reglas cargadas")
        for grupo, contenido in reglas.items():
            print(f"  • {grupo}: {len(contenido)} reglas")
    else:
        print("\n⚠️ No se pudieron recuperar las reglas")