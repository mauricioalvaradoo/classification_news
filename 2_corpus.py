import pickle
import re
from string import punctuation
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import CategorizedPlaintextCorpusReader
from nltk.tokenize import BlanklineTokenizer
# nltk.download('stopwords')
# nltk.download('punkt')


stops = stopwords.words('spanish')


# Corpus ================================================================================================
path_politica = 'news/politica/'
path_mundo    = 'news/mundo/'
path_economia = 'news/economia/'
path_deporte  = 'news/deporte/'
path_tech     = 'news/tech/'

corpus = CategorizedPlaintextCorpusReader(
    'news/',
    r'.*\.txt',
    cat_pattern=r'(.+)/.+',
    word_tokenizer=BlanklineTokenizer()
)


fileids    = corpus.fileids()
categorias = corpus.categories()
print(categorias)
print(len(categorias))
print(len(fileids))



# Exploración =============================================================================================
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
           w not in ['“', '”', '``', "''", '–', '‘', '’', '•']
    ]

    # Palabras más frecuentes por categoría
    freq = nltk.FreqDist(ws)
    words_more_freq = freq.most_common(20)

    print(f'TOP 20 palabras más frecuentes en {categoria}')
    for w, f in words_more_freq:
        print(f"{w}: {f}")

    print('\n ---------------------------------------- \n')



# Guardar corpus
with open('corpus.pkl', 'wb') as f:
    pickle.dump(corpus, f)

