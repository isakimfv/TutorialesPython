# Importamos las librerias correspondientes
import os                                               # Manejo de Archivos y operaciones de sistema
from dotenv import load_dotenv                          # Carga del archivo .env
from google import genai                                # Librería de Gemini

# Cargamos nuestra API_KEY de Gemini
load_dotenv()
# La almacenamos en una variable
API_KEY = os.getenv("API_KEY")

client = genai.Client(api_key = API_KEY) # Creas el cliente utilizando tu llave
response = client.models.generate_content(
    model="gemini-2.0-flash", contents="¿Cómo funciona la IA?"
)                                                   # Ejecutas la llamada a la API
print(response.text)                                # Muestras el resultado a partir del objeto