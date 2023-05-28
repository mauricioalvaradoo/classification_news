import pickle
import re
from string import punctuation
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import CategorizedPlaintextCorpusReader
from nltk.tokenize import BlanklineTokenizer
nltk.download('stopwords')
nltk.download('punkt')


stops = stopwords.words('spanish')
punto_junto = r'\b\w+\.\w*\b' # En caso que dos palabras estén juntas por un punto (es un error)



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
# print(fileids)
print(categorias)



# Exploración =============================================================================================
for categoria in categorias:

    files = corpus.fileids(categories=categoria)
    corpus_categoria = ""

    # No considerar las tres primeras filas del texto
    for f in files:
        content = corpus.raw(fileids=f)
        lines = content.split('\r\n')[3:]
        new_lines = BlanklineTokenizer().tokenize('\r\n'.join(lines))
        corpus_categoria += ' '.join(new_lines)

    # Transformaciones adicionales
    ws = re.sub(punto_junto, lambda m: m.group().replace('.', ''), corpus_categoria)
    ws = word_tokenize(ws.lower())
    ws = [
        w for w in ws
        if w not in stops and
           w not in punctuation and
           w not in ['“', '”', '``', "''", '–', '‘', '’', '•']
    ]

    # # Palabras más frecuentes por categoría
    freq = nltk.FreqDist(ws)
    words_more_freq = freq.most_common(20)

    print(f'TOP 20 palabras más frecuentes en {categoria}')
    for w, f in words_more_freq:
        print(f"{w}: {f}")

    print('\n ---------------------------------------- \n')



# Guardar corpus
with open('corpus.pkl', 'wb') as f:
    pickle.dump(corpus, f)

