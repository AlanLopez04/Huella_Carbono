import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json
import tempfile
import os
from typing import Dict, List, Any, Optional
from datetime import datetime # Importación necesaria para guardar la fecha

class FirebaseConnection:
    
    def __init__(self):
        self.db_ref = None
        
        # Intentar inicializar la app solo si no está inicializada
        if not firebase_admin._apps:
            self._initialize_app()
        
        # Asignar la referencia a la base de datos
        if firebase_admin._apps:
            try:
                # Obtener la referencia de la app por defecto
                self.db_ref = db.reference(app=firebase_admin.get_app())
            except Exception:
                self.db_ref = None
            

    def _initialize_app(self):
        """
        Método seguro para inicializar Firebase usando st.secrets en Streamlit Cloud.
        """
        temp_file_name = None
        try:
            # 1. OBTENER EL DICCIONARIO DEL SECRETO
            gcp_credentials_dict = st.secrets["gcp_service_account"]
            
            # CORRECCIÓN DE ATTRDICT A DICCIONARIO ESTÁNDAR
            standard_dict = dict(gcp_credentials_dict) 
            
            # 2. CREAR ARCHIVO TEMPORAL
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
                json.dump(standard_dict, temp_file)
                temp_file_name = temp_file.name 

            # 3. INICIALIZAR FIREBASE CON EL ARCHIVO TEMPORAL
            cred = credentials.Certificate(temp_file_name)
            
            database_url = 'https://calculadora-carbono-hidalgo-default-rtdb.firebaseio.com/' 
            
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            
        except KeyError:
            st.error("Error de Configuración: El secreto 'gcp_service_account' no se encontró. Verifica Streamlit Secrets.")
        except Exception as e:
            st.error(f"Error al inicializar Firebase: {e}")
        finally:
            # 4. LIMPIAR (Asegurar que el archivo temporal se elimine)
            if temp_file_name and os.path.exists(temp_file_name):
                os.unlink(temp_file_name)


    def get_rules_ref(self):
        """Devuelve la referencia al nodo principal de reglas."""
        if self.db_ref:
            # ✅ CORRECCIÓN CLAVE: Usamos 'reglas_produccion' según tu DB.
            return self.db_ref.child('reglas_produccion') 
        return None

    def obtener_reglas(self) -> Dict:
        """
        Obtiene todos los grupos de reglas de la base de datos.
        Esta función es la que llama motor_inferencia.py.
        """
        rules_ref = self.get_rules_ref()
        if rules_ref:
            # .get() trae todos los grupos: reglas_combinadas, reglas_energia, etc.
            data = rules_ref.get()
            return data if data else {}
        return {}
        
    def guardar_inferencia(self, usuario: str, conclusion: List[Dict]):
        """
        Guarda las conclusiones de la inferencia en Firebase.
        """
        if self.db_ref:
            timestamp = datetime.now().isoformat()
            self.db_ref.child('inferencias').push({
                'usuario': usuario,
                'fecha': timestamp,
                'conclusion': conclusion
            })
            print("✅ Conclusiones guardadas en Firebase.")