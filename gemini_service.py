# Promart AI - Versión Optimizada v1.1
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("No se encontró la API Key de Google en .env")

genai.configure(api_key=api_key)

def analyze_query_intent(user_query, user_answers=None):
    """
    Analiza si la consulta del usuario necesita clarificación o si está lista para búsqueda.
    Si user_answers está presente, asume que se está refinando una búsqueda previa.
    """
    print("🧠 Analizando intención de búsqueda...")
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    context = f"Consulta original: '{user_query}'"
    if user_answers:
        context += f"\nRespuestas de clarificación del usuario: {json.dumps(user_answers)}"
    
    prompt = f"""
    Eres un asistente experto de Promart. Tu trabajo es asegurar que el usuario encuentre EXACTAMENTE lo que necesita.
    
    Contexto:
    {context}
    
    Instrucciones:
    1. Si la consulta es VAGA (ej: "taladro", "pintura", "piso") y NO hay respuestas de clarificación:
       - Debes generar 2 o 3 preguntas cortas y clave para filtrar (ej: "¿Uso doméstico o profesional?", "¿Inalámbrico o con cable?").
       - Retorna JSON: {{ "type": "clarification", "questions": ["Pregunta 1", "Pregunta 2"] }}
       
    2. Si la consulta es ESPECÍFICA (ej: "taladro percutor dewalt 20v") O si hay respuestas de clarificación:
       - Genera un "refined_query" optimizado para el buscador de Promart (palabras clave precisas).
       - Retorna JSON: {{ "type": "search", "refined_query": "..." }}
    
    Responde SOLO con el JSON.
    """
    
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        print(f"❌ Error en Intent Analysis: {e}")
        # Fallback: asumir búsqueda directa
        return {"type": "search", "refined_query": user_query}

def analyze_products(user_query, products_json):
    """
    Analiza la lista de productos y devuelve el Top 3.
    """
    print("🧠 Analizando productos con Gemini...")
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    system_prompt = """
    Eres un Especialista Imparcial y Riguroso en productos de Promart.
    Tu misión es seleccionar las 4 MEJORES opciones de compra del JSON proporcionado.
    
    Reglas:
    1. Analiza TODOS los productos.
    2. Selecciona el Top 4 basándote en: Calidad/Precio, Adecuación a la búsqueda, y Valoraciones (si las hubiera, o marca).
    3. Clasifícalos con etiquetas como "Mejor Opción", "Mejor Precio", "Opción Profesional", "Alternativa Económica", etc.
    
    Formato JSON de Salida:
    {
        "titulo": "Aquí tienes las mejores opciones para: [Resumen Búsqueda]",
        "analisis_general": "[Breve resumen de 1 párrafo sobre lo encontrado]",
        "recomendaciones": [
            {
                "etiqueta": "[Ej: Mejor Opción Global]",
                "nombre": "[Nombre exacto]",
                "precio": "[Precio exacto]",
                "link": "[Link exacto]",
                "imagen": "[Link imagen]",
                "razon": "[Por qué lo elegiste en 1 frase]"
            },
            ... (Máximo 4 productos)
        ]
    }
    """
    
    user_message = f"""
    Solicitud del usuario: "{user_query}"
    
    Lista de productos disponibles (JSON):
    {json.dumps(products_json, ensure_ascii=False)}
    """
    
    try:
        response = model.generate_content(
            contents=[system_prompt, user_message],
            generation_config={"response_mime_type": "application/json"}
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        print(f"❌ Error en Gemini Product Analysis: {e}")
        return {
            "titulo": "Error en el análisis",
            "analisis_general": "Hubo un problema procesando tu solicitud.",
            "recomendaciones": []
        }
