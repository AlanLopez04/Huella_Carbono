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
        try:
            # 1. OBTENER EL DICCIONARIO DEL SECRETO (nombre del secreto que pegaste en Streamlit)
            gcp_credentials_dict = st.secrets["gcp_service_account"]
            
            # 2. CREAR ARCHIVO TEMPORAL
            # Firebase Admin SDK requiere la ruta a un archivo para initialize_app.
            # Creamos un archivo JSON temporal en el sistema de archivos de Streamlit.
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
                json.dump(gcp_credentials_dict, temp_file)
                temp_file_name = temp_file.name

            # 3. INICIALIZAR FIREBASE CON EL ARCHIVO TEMPORAL
            cred = credentials.Certificate(temp_file_name)
            
            # *** IMPORTANTE: AJUSTA LA URL DE LA BASE DE DATOS ***
            # Reemplaza 'TU_DATABASE_URL' con la URL real de tu Firebase Realtime Database
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://calculadora-carbono-hidalgo-default-rtdb.firebaseio.com/' 
                # ^ Asumo esta URL. ¡Verifícala en tu consola de Firebase!
            })
            
            # 4. LIMPIAR (Eliminar el archivo temporal inmediatamente)
            os.unlink(temp_file_name)
            
        except KeyError:
            # Error si el secreto no está configurado en Streamlit
            st.error("Error: El secreto 'gcp_service_account' no se encontró en Streamlit Secrets.")
        except Exception as e:
            # Capturar otros errores de conexión o inicialización
            st.error(f"Error al inicializar Firebase: {e}")


    def get_rules_ref(self):
        """Devuelve la referencia a la colección de reglas."""
        if self.db_ref:
            return self.db_ref.child('rules') 
        return None

# Puedes agregar otras funciones de la clase aquí si las tienes