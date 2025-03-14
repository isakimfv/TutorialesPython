# Importar librerías correspondientes
# Google Gemini API
from typing import Literal
from pydantic import BaseModel, Field
from google import genai

# Operaciones de sistema
import os
from dotenv import load_dotenv
import datetime

# Cargamos nuestra API_KEY de Gemini
load_dotenv()
API_KEY = os.getenv("API_KEY")
# Se define la variable global del modelo a utilizar en las requests
model="gemini-2.0-flash"

# Creamos la función que la LLM pueda ejectuar dependiendo de lo que el promp inicial indique
def get_calendar_event(date):
    """
    Función que simula la interacción con una API externa de un calendario
    """
    response = """
    Próximos Eventos:
    Reunión con Luis y María
    Fecha/Hora: 2025-03-13T16:00:00-04:00
    Ubicación: Sin ubicación
    Descripción: Reunión
    """
    return response

def get_weather(location):
    """
    Función que simula la interacción con una API meteorológica externa
    """
    response="""
    Llovizna
    28
    °C°F
    Prob. de precipitaciones: 35%
    Humedad: 69%
    Viento: a 8 km/h
    """
    return response



# Creamos un formato de respuesta para que la LLM pueda indicar qué tipo de solicitud está realizando el usuario y así determinar qué función es necesaria
class TipoSolicitudPrimaria(BaseModel):
    """ Llamada enrutadora a la LLM: Contiene qué tipo de solitud primaria está siendo realizada"""

    tipo_solicitud: Literal["extraer_evento_calendario", "clima","otro"] = Field(
        description="Tipo de solicitud primaria realizada"
    )
    confianza: float = Field(description="Puntuación de confianza del 0 al 1")
    descripcion: str = Field(description="Descripción de la solicitud")

# Creamos un formato para los datos que necesita la función de extracción de eventos
class fecha(BaseModel):
    """Detalles para la extracción de eventos"""
    dia: int = Field(description="Dia de la fecha")
    mes: int = Field(description="Mes de la fecha")
    ano: int = Field(description="Año de la fecha")

# Creamos un formato para los datos que necesita la función de extracción del clima
class ubicacion(BaseModel):
    """ Detalles de una ubicación"""
    latitud: int = Field(description="Latitud de una localidad")
    longitud: int = Field(description="Longitud de una localidad")



# Creamos la función que le solicita a la LLM determina qué tipo de solicitud está siendo realizada
def enruta_solicitud(user_input: str) -> TipoSolicitudPrimaria:
    """ Enruta la llamada a la LLM para determinar el tipo de solicitud"""
    print("Enrutando la solicitud primaria")
    
    client = genai.Client(api_key=API_KEY)
    system_instructions="Determina si la solicitud del usuario está relacionada con los calendarios o con extracción de información"
    response = client.models.generate_content(
        model=model,
        contents=f"{system_instructions}\n\nMensaje Ususario: {user_input}",
        config = { 
            "response_mime_type" : 'application/json',
            "response_schema" : TipoSolicitudPrimaria
        },        
    )
    result : TipoSolicitudPrimaria = response.parsed
    print(f"Solicitud enrutada como: {result.tipo_solicitud} con una confianza de: {result.confianza}")
    return result

# Creamos la función que se encarga de manejar la solicitud de obtención de eventos para una fecha. Incluyendo la extracción de los datos necesarios para llamar a la función
def manejar_get_evento(description: str):
    """Procesa la extracción de un evento"""
    print("Procesando una solicitud de extracción de eventos")
    today = datetime.datetime.today()       # Crear la fecha actual
    client = genai.Client(api_key=API_KEY)  # Crea el cliente de la API
    
    # Se definen las instrucciones que guiarán a la LLM en la extracción de la fecha del mensaje del usuario
    system_instructions=f"La fecha actual es {today.day} del mes {today.month} del año {today.year}. En referencia a la fecha actual, extrae la fecha a la que se refiere el usuario. "
    response = client.models.generate_content(
        model=model,
        contents=f"{system_instructions}\n\nMensaje Usuario: {description}",
        config = { 
            "response_mime_type" : 'application/json',
            "response_schema" : fecha
        }        
    )
    # Se reciben los datos de la fecha en el formato fecha 
    details : fecha = response.parsed
    print(f"Extrayendo los eventos para: {details.ano}-{details.mes}-{details.dia}")
    # Se llama a la función con los datos de la fecha
    events = get_calendar_event(f"{details.ano}-{details.mes}-{details.dia}")
    # Genera respuesta
    return events

# Creamos la función que se encarga de manejar la obtención de datos del clima de la api, incluyendo la extracción de los datos necesarios para la llamar a la función.
def manejar_get_clima(description: str):
    """Procesa la obtención del clima"""
    print("Procesando una solicitud de extracción de eventos")
    today = datetime.datetime.today()       # Crear la fecha actual
    client = genai.Client(api_key=API_KEY)  # Crea el cliente de la API
    
    # Se definen las instrucciones que guiarán a la LLM en la extracción de la fecha del mensaje del usuario
    system_instructions=f"La fecha actual es {today.day} del mes {today.month} del año {today.year}. Identifica la latitud y longitud de la ciudad o país mencionado en el mensaje del usuario."
    response = client.models.generate_content(
        model=model,
        contents=f"{system_instructions}\n\nMensaje Usuario: {description}",
        config = { 
            "response_mime_type" : 'application/json',
            "response_schema" : ubicacion
        }        
    )
    # Se reciben los datos de la fecha en el formato fecha 
    details : ubicacion = response.parsed
    print(f"Obteniendo el clima para: {details.latitud}|{details.longitud}")
    # Se llama a la función con los datos de la fecha
    events = get_weather(f"{details.latitud}|{details.longitud}")
    # Genera respuesta
    return events

# Se define la función que enruta a la LLM entre la obtención de eventos y de clima
def procesar_solicitud_primaria(user_input: str):
    """Funcion principal para implementar el enrutamiento del trabajo"""
    print("Procesando solicitud primaria")

    # Enrutar la solicitud
    route_result = enruta_solicitud(user_input)

    # Evaluamos el grado de confianza del modelo
    if route_result.confianza < 0.7:
        print(f"Grado de confianza bajo: {route_result.confianza}")
        return None
    
    # Enrutar el handler apropiado
    if route_result.tipo_solicitud == "extraer_evento_calendario":
        return manejar_get_evento(route_result.descripcion)
    elif route_result.tipo_solicitud == "clima":
        return manejar_get_clima(route_result.descripcion)
    else:
        print("Tipo de solicitud no soportada")
        return None

# Probamos al agente con un mensaje de prueba
input = "¿Qué eventos tengo para el jueves?"
result = procesar_solicitud_primaria(input)
print(result)
"""
-------------------------------------------------------------
Output:
Procesando solicitud primaria
Enrutando la solicitud primaria
Solicitud enrutada como: extraer_evento_calendario con una confianza de: 0.95
Procesando una solicitud de extracción de eventos
Extrayendo los eventos para: 2025-3-20
    Próximos Eventos:
    Reunión con Luis y María
    Fecha/Hora: 2025-03-13T16:00:00-04:00
    Ubicación: Sin ubicación
    Descripción: Reunión
"""

# Probamos al agente con otro tipo de mensaje
input = "¿Cuál es el clima de Caracas hoy?"
result = procesar_solicitud_primaria(input)
print(result)
"""
-------------------------------------------------------------
Output:
Procesando solicitud primaria
Enrutando la solicitud primaria
Solicitud enrutada como: clima con una confianza de: 0.95
Procesando una solicitud de extracción de eventos
Obteniendo el clima para: 10|-66
    Llovizna
    28
    °C°F
    Prob. de precipitaciones: 35%
    Humedad: 69%
    Viento: a 8 km/h
"""