import random
import time
from playwright.sync_api import sync_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
]

def search_promart(query):
    """
    Busca productos en Promart.pe y retorna una lista de diccionarios.
    """
    print(f"🔎 Buscando en Promart: {query}")
    
    with sync_playwright() as p:
        # Optimización para Render: usar menos memoria
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-dev-shm-usage',  # Evita problemas de memoria compartida
                '--no-sandbox',              # Necesario para contenedores
                '--disable-setuid-sandbox',
                '--disable-gpu',             # No necesitamos GPU
                '--disable-software-rasterizer',
                '--single-process'           # Usa un solo proceso (menos memoria)
            ]
        )
        context = browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            # Optimización: Ir directamente a la URL de búsqueda (más rápido y confiable)
            print(f"🔍 Buscando directamente: {query}")
            search_url = f"https://www.promart.pe/busca?ft={query}"
            page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
            
            # Espera reducida para renderizado de JS
            print("⏳ Esperando resultados...")
            time.sleep(3)  # Reducido de 5 a 3 segundos
            
            # 4. Parsear con BeautifulSoup
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page.content(), 'html.parser')
            
            products_data = []
            
            # Estrategia: Buscar enlaces que parezcan de productos
            # En Promart los links de producto suelen tener /p al final o estructura similar
            # Buscamos contenedores que tengan precio y titulo
            
            # Intentamos identificar contenedores de producto por clases comunes en VTEX/Promart
            # A veces son <li> o <div> con clases como 'product-item', 'vtex-product-summary', etc.
            
            # Buscamos todos los links
            links = soup.find_all('a', href=True)
            
            seen_urls = set()
            
            for link in links:
                href = link['href']
                # Filtrar links relevantes (que no sean js, vacíos, o categorías genéricas si es posible)
                if '/p' in href and href not in seen_urls:
                    # Este link podría ser un producto.
                    # Vamos a intentar sacar info de sus hijos o padres.
                    
                    # A veces el link envuelve todo, a veces solo el titulo o imagen.
                    # Busquemos el contenedor padre inmediato o abuelo
                    card = link.find_parent('div', class_=lambda x: x and 'product' in x.lower())
                    if not card:
                        card = link.find_parent('li')
                    
                    if not card:
                        continue
                        
                    # Dentro del card, buscamos titulo, precio, imagen
                    # Titulo: suele ser un h3, h4, span o el mismo texto del link
                    title_el = card.find(lambda tag: tag.name in ['span', 'h3', 'div'] and ('brand' in str(tag.get('class', '')).lower() or 'name' in str(tag.get('class', '')).lower()))
                    if not title_el:
                         title_el = card.find('div', class_='product-name') # Intento generico
                    
                    name = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)
                    
                    # Precio - Mejorado para capturar descuentos y precios web
                    # Estrategia: Buscar TODOS los elementos de precio y tomar el más bajo (precio final)
                    price_elements = card.find_all(lambda tag: tag.name in ['span', 'div'] and 
                                                    ('price' in str(tag.get('class', '')).lower() or 
                                                     'currency' in str(tag.get('class', '')).lower() or
                                                     'precio' in str(tag.get('class', '')).lower()))
                    
                    prices = []
                    for price_el in price_elements:
                        price_text = price_el.get_text(strip=True)
                        # Extraer solo números y punto decimal
                        import re
                        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if price_match:
                            try:
                                price_value = float(price_match.group().replace(',', ''))
                                prices.append((price_value, price_text))
                            except:
                                pass
                    
                    # Tomar el precio más bajo (que suele ser el precio con descuento o web)
                    if prices:
                        prices.sort(key=lambda x: x[0])  # Ordenar por valor numérico
                        price = prices[0][1]  # Tomar el texto del precio más bajo
                    else:
                        price = "Consultar"
                    
                    # Imagen
                    img_el = card.find('img')
                    img_src = img_el['src'] if img_el and 'src' in img_el.attrs else ""
                    
                    # Validacion basica
                    if len(name) > 5 and (price != "Consultar" or img_src):
                        full_link = href if href.startswith('http') else f"https://www.promart.pe{href}"
                        
                        products_data.append({
                            "id": f"p-{len(products_data)}",
                            "nombre": name,
                            "precio_actual": price,
                            "link_producto": full_link,
                            "imagen": img_src,
                            "detalles_clave": f"Producto: {name}"
                        })
                        seen_urls.add(href)
                        
                        if len(products_data) >= 20:
                            break
            
            print(f"✅ Encontrados {len(products_data)} productos.")
            return products_data
            
        except Exception as e:
            print(f"❌ Error en scraping: {e}")
            return []
        finally:
            browser.close()

if __name__ == "__main__":
    # Test rápido
    res = search_promart("taladro")
    print(res)
