import pickle, gzip
import pandas as pd
import numpy as np
import re
from string import punctuation
import nltk
from nltk.corpus import stopwords
from nltk.corpus import CategorizedPlaintextCorpusReader
from nltk.tokenize import BlanklineTokenizer
# nltk.download('stopwords')
# nltk.download('punkt')

stops = stopwords.words('spanish')



# Corpus ================================================================================================
'''
path_politica = 'news/politica/'
path_mundo    = 'news/mundo/'
path_economia = 'news/economia/'
path_deporte  = 'news/deporte/'
path_tech     = 'news/tech/'
'''

corpus = CategorizedPlaintextCorpusReader(
    'news/',
    r'.*\.txt',
    cat_pattern=r'(.+)/.+',
    word_tokenizer=BlanklineTokenizer()
)


# Guardar corpus
with gzip.open('corpus.pkl.gz', 'wb') as f:
    pickle.dump(corpus, f)



# Definición ==============================================================================================
last_day = '02/09/2023'

fileids    = corpus.fileids()
categorias = corpus.categories()
news_per_cat = pd.DataFrame([{'Categoria': c, 'Noticias': len(corpus.fileids(c))} for c in categorias])
news_per_cat.set_index('Categoria', inplace=True)
news_per_cat['% Total'] = np.round(news_per_cat['Noticias']/news_per_cat['Noticias'].sum()*100, 1)



# Estadística =============================================================================================
print('')
print(f'Categorias: {categorias}')
print(f'Noticias:   {len(fileids)}')
print('')
print(f'{news_per_cat}')
print('')

with open('most_frequent_words.txt', 'w') as file:
    for categoria in categorias:
        ws = []
    
        files = corpus.fileids(categories=categoria)
        for f in files:
            # Transformaciones adicionales
            texto = corpus.raw(f)
            ws += re.findall(r'\w+', texto.lower())
    
        stops = set(stopwords.words('spanish'))
        ws = [
            w for w in ws
            if w not in stops and
               w not in punctuation and
               w not in ['“', '”', '``', "''", '–', '‘', '’', '•'] and
               str(w).isalpha() == True and
               w not in ['si', 'dijo', 'así', 'cómo']
        ]
    
        # Palabras más frecuentes por categoría
        freq = nltk.FreqDist(ws)
        words_more_freq = freq.most_common(20)
    
        # Guardar en archivo
        file.write(f'TOP 20 palabras más frecuentes en {categoria}\n')
        for w, f in words_more_freq:
            file.write(f'{w}: {f}\n')
        file.write('\n --------------------------------------------------- \n')
        
        # Imprimir en pantalla
        print(f'TOP 20 palabras más frecuentes en {categoria}')
        for w, f in words_more_freq:
            print(f'{w}: {f}')
        print('\n --------------------------------------------------- \n')

    file.write(f'\n Actualizado con noticias hasta {last_day} \n')


news_per_cat.to_json('news_per_category.json', indent=3)

