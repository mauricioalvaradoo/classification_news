# pip install webdriver_manager
import re, time, json
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager



# Declaración de funciones ====================================================
def get_urls_news(date):
    ''' Consigue los 'urls' de cada noticia para una fecha definida
     
    Parámetros
    -----------
    date[str]: día deseado. ejemplo: '2023-05-27'
        
    Retorno
    ----------
    cat_urls[list]: dictionario de urls
    
    '''
    
    chrome_service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service)
    
    url = f'https://elcomercio.pe/archivo/todas/{date}/'
    driver.get(url)
    
    
    try:
        driver.get(url)
        
        html_to_scroll = driver.find_element(By.XPATH, '//body')
        scrolls = 0
        page_height = driver.execute_script('return document.body.scrollHeight')
        while scrolls < page_height:
            html_to_scroll.send_keys(Keys.PAGE_DOWN)
            scrolls += 400
            time.sleep(0.2)
        
        
        html = driver.page_source
        driver.quit()
        
        soup = BeautifulSoup(html, 'html.parser')
        divs = soup.find_all('div', class_='story-item')
        news = []
    
        for div in divs:
            new = div.find('a', class_='story-item__title').get('href')

            if new.startswith(
                    (
                        '/politica/', '/economia/', '/mundo/',
                        '/deporte-total/', '/tecnologia/'
                    )
            ):
                news.append(f'https://elcomercio.pe{new}')
    
        
        cat_urls = {
            'politica': [],
            'economia': [],
            'mundo':    [],
            'deporte':  [],
            'tech':     []
        }
        
        for url in news:
            if '/politica/' in url:
                cat_urls['politica'].append(url)
            elif '/economia/' in url:
                cat_urls['economia'].append(url)
            elif '/mundo/' in url:
                cat_urls['mundo'].append(url)
            elif '/deporte-total/' in url:
                cat_urls['deporte'].append(url)
            elif '/tecnologia/' in url:
                cat_urls['tech'].append(url)

        return cat_urls
    
    except Exception as e:
        print(f'Error: {str(e)}')




def text_processing(text):
    ''' Procesamiento del texto

    Parámetros
    -----------
    texto[soup]: Texto scrapeado

    Retorno
    ----------
    texto_clean[str]: Texto sin anuncios, títulos, links, etc.
    
    '''

    # Eliminando título de contenido
    try: 
        header = text.find_all('h2', {'class': 'story-contents__header'})
        for i in header:
            i.decompose()
    except:
        pass

    # Eliminando anuncios en el texto
    try: 
        adds = text.find_all('blockquote', {'class': 'story-contents__blockquote'})
        for i in adds:
            i.decompose()
    except:
        pass

    # Eliminando Twitter
    try:
        tweet = text.find_all('div', {'class': 'story-contents__embed embed-script'})
        for i in tweet:
            i.decompose()
    except:
        pass

    # Eliminando link list
    try:
        links1 = text.find_all('div', {'class': 'link-list'})
        links2 = text.find_all('div', {'class': 'live-event2-comment'})
        # links3 = text.find_all('ul', {'class': 'story-contents__paragraph-list'})
                
        all_links = links1 + links2 # + links3
        for i in all_links:
            i.decompose()
    except:
        pass

    # Eliminar pies de imágenes
    try:
        captions = text.find_all('figcaption', {'class': 'story-contents__caption'})
        for i in captions:
            i.decompose()
    except:
        pass
    
    
    texto_clean= text.get_text(separator=' ') # Espacios en saltos de párrafo
    texto_clean = texto_clean.strip()
    
    return texto_clean



def save_text_from_news(date):
    ''' Guarda archivos de texto de cada noticia
    
    Parámetros
    -----------
    date[str]: día deseado. ejemplo: '2023-05-27'

    '''

    print(f'... Scrapeando a El Comercio. Fecha consultada: {date} ...')    

    dict_urls = get_urls_news(date=date)

    control = {}    

    for cat, urls in dict_urls.items():
        
        for url in urls:
            try:
                
                html = requests.get(url)
                soup = BeautifulSoup(html.content, 'html.parser')
    
                # Titulo
                try:
                    # Normal
                    title = soup.find('h1', {'class': 'sht__title'}).text
                except:
                    # Para suscriptores
                    title = soup.find('h1', {'class': 'story-header-title'}).text
                            
                # Texto
                text  = soup.find('div', {'class': 'story-contents__content'})
                
                # Eliminación de contenido no relevante
                texto_clean = text_processing(text)
    
                # Guardar en un 'txt'
                title_for_file = re.sub(r'[^a-zA-Z0-9]', '', title)
                file_name = f'{date}-{title_for_file}'
                
                # Puede que en las 'noticias para suscriptores' no se haya extraido nada
                if len(texto_clean) != 0:
                    with open(f'news/{cat}/{file_name}.txt', 'w', encoding='utf-8') as f:
                        f.write(texto_clean)
                
                control[file_name] = url
                
            except:
                pass
    
    with open(f'control/{date}.json', 'w') as f: 
        json.dump(control, f, ensure_ascii=False, indent=2)




# Extracción de noticias ======================================================
ini = datetime(2023,4,5)
fin = datetime(2023,9,23)

lista_fechas = [
    (ini + timedelta(days=d)).strftime('%Y-%m-%d')
        for d in range((fin - ini).days + 1)
] 

for i in lista_fechas:
    save_text_from_news(date=i)

