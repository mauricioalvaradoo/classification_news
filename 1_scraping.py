import pandas as pd
from datetime import datetime
import re
from bs4 import BeautifulSoup
import requests



# Declaración de funciones ===========================================================================

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



def save_text_from_news(urls, src):
    ''' Guarda archivos de texto de cada noticia
    
    Parámetros
    -----------
    urls[list]: urls de noticias
    src[str]: nombre de la ruta donde se guarda el texto

    '''

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

            # Eliminando anuncios en el texto
            try: 
                adds = text.find_all('blockquote', {'class': 'story-contents__blockquote'})
                for i in adds:
                    i.decompose()
                text_no_adds = text.text
            except:
                text_no_adds = text.text

            # Guardar en un 'txt'
            title_for_file = re.sub(r'[^a-zA-Z0-9]', '', title)
            file_name = f'{day}-{title_for_file}'
            
            if len(text_no_adds) != 0: # Puede que en las 'noticias para suscriptores' no se haya extraido nada
                with open(f'news/{src}/{file_name}.txt', 'w', encoding='utf-8') as f:
                    f.write(src.upper() + '\n')
                    f.write(title + '\n')
                    f.write(time + '\n')
                    f.write(text_no_adds)
        
        except:
            pass



# Extracción de información ==========================================================================
date_to_consult = '28/05/2023' # Máximo 4 días hacia atrás (aprox. 100 noticias)


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

