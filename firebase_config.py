import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json
import tempfile
import os

class FirebaseConnection:
    
    def __init__(self):
        self.db_ref = None
        
        # Intentar inicializar la app solo si no está inicializada
        if not firebase_admin._apps:
            self._initialize_app()
        
        # Asignar la referencia a la base de datos
        if firebase_admin._apps:
            self.db_ref = db.reference()
            

    def _initialize_app(self):
        """
        Método seguro para inicializar Firebase usando st.secrets en Streamlit Cloud.
        """
        temp_file_name = None
        try:
            # 1. OBTENER EL DICCIONARIO DEL SECRETO
            gcp_credentials_dict = st.secrets["gcp_service_account"]
            
            # 💡 CORRECCIÓN CLAVE: CONVERTIR AttrDict A DICCIONARIO ESTÁNDAR
            # Usamos .to_dict() para que la biblioteca 'json' lo pueda manejar.
            standard_dict = dict(gcp_credentials_dict) 
            
            # 2. CREAR ARCHIVO TEMPORAL
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
                # Usar el diccionario estándar para la serialización
                json.dump(standard_dict, temp_file)
                temp_file_name = temp_file.name 

            # 3. INICIALIZAR FIREBASE CON EL ARCHIVO TEMPORAL
            cred = credentials.Certificate(temp_file_name)
            
            # MUY IMPORTANTE: VERIFICAR LA URL
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
        """Devuelve la referencia a la colección de reglas."""
        if self.db_ref:
            return self.db_ref.child('rules') 
        return None

# Puedes agregar otras funciones de la clase aquí si las tienes