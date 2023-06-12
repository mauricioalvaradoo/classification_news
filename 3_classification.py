import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix

from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Embedding, Flatten, Bidirectional, LSTM # ConvLSTM2D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.optimizers import Adam



# Recuperar el corpus =======================================================================================
with open('corpus.pkl', 'rb') as f:
    corpus = pickle.load(f)

categories = corpus.categories() 
print(categories)
print(len(categories))


# Train test split ==========================================================================================
X_train = []; X_test  = []; y_train = []; y_test  = []

for cat in categories:
    files = corpus.fileids(categories=cat)
    train_files, test_files = train_test_split(files, test_size=0.3, random_state=19)
    
    # Unión de palabras en documentos
    train_documents = [' '.join(corpus.words(fileids=f)) for f in train_files]
    test_documents  = [' '.join(corpus.words(fileids=f)) for f in test_files ]
    
    X_train.extend(train_documents)
    X_test.extend(test_documents)
    y_train.extend([cat] * len(train_documents))
    y_test.extend([cat] * len(test_documents))


# Procesamiento de texto ====================================================================================
labels = LabelEncoder()
y_train_encoded = labels.fit_transform(y_train)
y_test_encoded = labels.transform(y_test)

tokenizer = Tokenizer()
tokenizer.fit_on_texts(X_train)

vocab_size = len(tokenizer.word_index) + 1

X_train = tokenizer.texts_to_sequences(X_train)
X_test  = tokenizer.texts_to_sequences(X_test)
X_train = pad_sequences(X_train)
X_test  = pad_sequences(X_test)

'''
print(X_train)
print(y_train)
print(X_test)
print(y_test)
print(vocab_size)
'''


# Modelo de red neuronal ConvLSTM ===========================================================================
model = Sequential(
    [
        Embedding(vocab_size, 64),
        Bidirectional(LSTM(64, return_sequences=True)),
        Bidirectional(LSTM(32)),
        # ConvLSTM2D(filters=64, kernel_size=(1, 1), activation='relu', padding='same', return_sequences=True),
        # ConvLSTM2D(filters=32, kernel_size=(1, 1), activation='relu', padding='same'),
        Flatten(),
        Dense(64, activation='relu'),
        Dense(32, activation='relu'),
        Dense(5, activation='linear')
    ]
)
# print(model.summary())

model.compile(
    loss=SparseCategoricalCrossentropy(from_logits=True),
    optimizer=Adam(0.005),
    metrics=['mean_squared_error', 'accuracy']
)

results = model.fit(
    X_train, np.array(y_train_encoded),
    epochs=20,
    verbose=2,
    validation_data=(X_test, np.array(y_test_encoded))
)



# Visualizaciones ============================================================================================
plt.plot(results.history['accuracy'])
plt.plot(results.history['val_accuracy'])
plt.xlabel('epochs')
plt.ylabel('accuracy')
plt.legend(['accuracy', 'val_accuracy'])
plt.show()

plt.plot(results.history['loss'])
plt.plot(results.history['val_loss'])
plt.xlabel('epochs')
plt.ylabel('loss')
plt.legend(['loss', 'val_loss'])
plt.show()


# Matriz de confusión
y_hat = model.predict(X_test)
y_hat = np.argmax(y_hat, axis=1)

confusion_matrix = confusion_matrix(y_test_encoded, y_hat)
sns.heatmap(confusion_matrix, annot=True, cmap='Blues')
plt.xlabel('Estimado')
plt.ylabel('Real')
plt.show()


# Guardado
model.save('model.h5')