from datetime import datetime
import re
import csv
from bs4 import BeautifulSoup
import requests



# Declaración de funciones ===========================================================================================

def get_urls_news(cat, date):
    ''' Consigue los 'urls' de cada noticia para una fecha definida
    
    Parámetros
    -----------
    cat[str]: categoría de la noticia. las permitidas son las siguientes:
        -- politica
        -- mundo
        -- economia
        -- deporte-total
        -- tecnologia
    
    date[str]: día deseado. ejemplo: '27/05/2023'
        
    Retorno
    ----------
    news[list]: urls
    '''

    base = 'https://elcomercio.pe/archivo/'
    url  = f'{base}{cat}/'
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser').find('div', {'role': 'main'})

    # Noticias
    divs = soup.find_all('div', {'class': 'story-item'})
    news = []

    for div in divs:
        date_in_div = div.find('span', {'class': 'story-item__date-time'})
        
        # Solo noticias del dia deseado
        if date_in_div and date in date_in_div.text:
            new = div.find('a', {'class': 'story-item__title'}).get('href')
            news.append(f'https://elcomercio.pe/{new}')

    return news



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



def save_text_from_news(urls, src):
    ''' Guarda archivos de texto de cada noticia
    
    Parámetros
    -----------
    urls[list]: urls de noticias
    src[str]: nombre de la ruta donde se guarda el texto

    '''

    full = []
    news_scrapped = set()

    # Existencias en control.csv
    try:
        with open('news/control.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)
            for row in reader:
                title = row[0]
                day = row[1]
                news_scrapped.add((title, day))  # Agregar título y día al conjunto de noticias ya scrapeadas
    except FileNotFoundError:
        pass


    for url in urls:
        
        try:
            html = requests.get(url)
            soup = BeautifulSoup(html.content, 'html.parser')

            # Titulo
            try:
                title = soup.find('h1', {'class': 'sht__title'}).text # Normal
            except:
                title = soup.find('h1', {'class': 'story-header-title'}).text # Para suscriptores
                        
            # Texto
            text  = soup.find('div', {'class': 'story-contents__content'})
            # Tiempo
            time  = soup.find('time').text
            day   = time.split()[0]
            try: # Fechas mal formateadas
                day = datetime.strptime(day, '%d/%m/%Y').strftime('%Y_%m_%d')
            except:
                day = '_'.join(day.split('/')[::-1])
            hour  = time.split()[1]

            # Obviar noticias ya scrapeadas anteriormente del día
            if (title, day) in news_scrapped:
                continue
            
            # Eliminación de contenido no relevante
            texto_clean = text_processing(text)

            # Guardar en un 'txt'
            title_for_file = re.sub(r'[^a-zA-Z0-9]', '', title)
            file_name = f'{day}-{title_for_file}'
            
            if len(texto_clean) != 0: # Puede que en las 'noticias para suscriptores' no se haya extraido nada
                with open(f'news/{src}/{file_name}.txt', 'w', encoding='utf-8') as f:
                    f.write(texto_clean)
    
                new = [title, day, src, file_name, url]
                full.append(new)
        
        except:
            pass


    # Control
    if full:
        with open('news/control.csv', 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            if f.tell() == 0:
                writer.writerow(['Titulo', 'Fecha', 'Categoria', 'Título del archivo', 'Url'])
            writer.writerows(full)




# Extracción de información ==========================================================================================
# Máximo 4 días hacia atrás (aprox. 100 noticias). 'Mundo' y 'deporte' alcanzan 100 noticias en 2 días. 
date_to_consult = '16/07/2023'


urls_politica = get_urls_news(cat='politica', date=date_to_consult)
urls_mundo    = get_urls_news(cat='mundo', date=date_to_consult)
urls_economia = get_urls_news(cat='economia', date=date_to_consult)
urls_deporte  = get_urls_news(cat='deporte-total', date=date_to_consult)
urls_tech     = get_urls_news(cat='tecnologia', date=date_to_consult)

save_text_from_news(urls_politica, src='politica')
save_text_from_news(urls_mundo, src='mundo')
save_text_from_news(urls_economia, src='economia')
save_text_from_news(urls_deporte, src='deporte')
save_text_from_news(urls_tech, src='tech')

