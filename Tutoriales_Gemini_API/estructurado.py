# Importamos las librerias correspondientes
import os                                              # Manejo de Archivos y operaciones de sistema
from dotenv import load_dotenv         # Carga del archivo .env
from google import genai                    # Librería de Gemini

# Cargamos nuestra API_KEY de Gemini
load_dotenv()
# La almacenamos en una variable
API_KEY = os.getenv("API_KEY")

prompt = """Enumere algunas series de televisión populares del año 2025 en formato JSON.

Utilice este esquema JSON:

serie = {'nombre': str, 'descripcion': str, 'reparto':List[str]}
Return: list[serie]"""

client = genai.Client(api_key=API_KEY)
response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents=prompt,
)

# Utilice la respuesta como una cadena JSON.
print(response.text)
