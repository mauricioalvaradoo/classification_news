# Clasificación de noticias de El Comercio
En el periódico El Comercio, las principales categorías de las noticias son las siguientes:
- Política
- Mundo
- Economía
- Deportes
- Tecnología

Para el proceso de clasificación se requiere 
1. [Extraer el contenido de cada una de la noticias](https://github.com/mauricioalvaradoo/classification_news/blob/master/1_scraping.py), mediante web scraping.
2. [Crear un corpus](https://github.com/mauricioalvaradoo/classification_news/blob/master/2_corpus.py), en el que se categoriza todas las noticias según temática.
3. [Crea una red neuronal recurrente](https://github.com/mauricioalvaradoo/classification_news/blob/master/3_classification.py), que interprete el contexto de las noticias.

Cada noticia fue almacenada en las siguientes rutas:
- [news/politica](https://github.com/mauricioalvaradoo/classification_news/blob/master/news/politica)
- [news/mundo](https://github.com/mauricioalvaradoo/classification_news/blob/master/news/mundo)
- [news/economia](https://github.com/mauricioalvaradoo/classification_news/blob/master/news/economia)
- [news/deporte](https://github.com/mauricioalvaradoo/classification_news/blob/master/news/deporte)
- [news/tech](https://github.com/mauricioalvaradoo/classification_news/blob/master/news/tech)
