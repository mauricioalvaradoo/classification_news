import pandas as pd
import pickle

from nltk.tokenize import BlanklineTokenizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from tensorflow.keras import Sequential
from tensorflow.keras.layers import (
    Dense, Conv2D, Bidirectional, Flatten, Embedding, LSTM
)
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.optimizers import Adam

seed = 19



# Recuperar el corpus =======================================================================================
with open('corpus.pkl', 'rb') as f:
    corpus = pickle.load(f)


# No considerar las tres primeras filas =====================================================================
def custom_tokenizer(text):
    lines = text.split('\r\n')[3:]
    new_lines = BlanklineTokenizer().tokenize('\r\n'.join(lines))
    return new_lines

corpus_tok = custom_tokenizer(corpus.raw())


# Train-test split ==========================================================================================
print(len(corpus_tok))
print(len(corpus.categories()))


X_train, X_test, y_train, y_test = \
    train_test_split(corpus_tok, corpus.categories(), test_size=0.2, random_state=seed)


# Procesamiento de texto ====================================================================================
labels = LabelEncoder()
y_train_encoded = labels.fit_transform(y_train)
y_test_encoded = labels.transform(y_test)

tokenizer = Tokenizer()
tokenizer.fit_on_texts(X_train)

vocabulario = len(tokenizer.word_index) + 1

X_train = tokenizer.texts_to_sequences(X_train)
X_test = tokenizer.texts_to_sequences(X_test)
X_train = pad_sequences(X_train)
X_test = pad_sequences(X_test)


# Modelo de red neuronal ConvLSTM ===========================================================================
model = Sequential([
    Embedding(vocabulario, 64),
    Bidirectional(LSTM(64, return_sequences=True)),
    Bidirectional(LSTM(32)),
    Dense(64, activation='relu'),
    Dense(5, activation='linear')
])

model.compile(
    loss=SparseCategoricalCrossentropy(from_logits=True),
    optimizer=Adam(0.001),
    metrics=['mean_squared_error', 'accuracy']
)

results = model.fit(
    X_train, y_train,
    epochs=10,
    verbose=10,
    validation_data=(X_test, y_test)
)





