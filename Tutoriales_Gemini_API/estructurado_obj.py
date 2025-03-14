# Importamos las librerias correspondientes
import os                                   # Manejo de Archivos y operaciones de sistema
from dotenv import load_dotenv              # Carga del archivo .env
from google import genai                    # Librería de Gemini
from pydantic import BaseModel

# Cargamos nuestra API_KEY de Gemini
load_dotenv()
# La almacenamos en una variable
API_KEY = os.getenv("API_KEY")

# Creamos el objeto para el formato de respuesta
class serie(BaseModel):
    nombre : str            # Nombre de la serie
    descripcion : str       # Descripción de la serie
    reparto : list[str]     # Reparto de actores

# Definimos el prompt
prompt = "Enumere algunas series de televisión populares del año 2025 en formato JSON."

# Creamos el cliente con la llave
client = genai.Client(api_key=API_KEY)

#Recibimos la respuesta
response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents=prompt,
    # Definimos la configuración de la llamada
    config = {
        # Tipo de respuesta -> JSON
        "response_mime_type": "application/json",
        # Formato de respuesta -> Una lista del Objeto creado
        "response_schema":list[serie],
    }
)

# Instanciamos la respuesta como el objeto correspondiente
series: list[serie] = response.parsed

# Mostramos respuesta
print(series)
