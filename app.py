from flask import Flask, render_template, request, jsonify
from scraper import search_promart
from gemini_service import analyze_products, analyze_query_intent
import os

app = Flask(__name__)

@app.after_request
def set_csp(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' https: data:; connect-src 'self'"
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json
    user_query = data.get('query')
    user_answers = data.get('answers') # Lista de respuestas si las hay
    
    if not user_query:
        return jsonify({"error": "Query vacía"}), 400
    
    # 1. Analizar Intención (Solo si no estamos ya en flujo de respuestas)
    # Si hay respuestas, asumimos que queremos buscar directamente usando esas respuestas
    
    intent_data = analyze_query_intent(user_query, user_answers)
    
    if intent_data.get("type") == "clarification":
        return jsonify({
            "type": "clarification",
            "questions": intent_data.get("questions", [])
        })
        
    # Si es tipo "search", procedemos
    search_term = intent_data.get("refined_query", user_query)
    print(f"🚀 Iniciando búsqueda con término refinado: {search_term}")
    
    # 2. Scraping
    products = search_promart(search_term)
    
    if not products:
        return jsonify({
            "type": "error",
            "message": "No pudimos encontrar productos en Promart que coincidan con tu búsqueda. Intenta con términos más generales."
        })
    
    # 3. Análisis IA (Top 3)
    recommendation = analyze_products(user_query + (f" Contexto: {user_answers}" if user_answers else ""), products)
    
    # Añadimos el tipo para el frontend
    recommendation["type"] = "result"
    return jsonify(recommendation)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
