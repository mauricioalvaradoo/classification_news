import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import gzip

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix, roc_curve, auc

from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Embedding, Flatten, Bidirectional, LSTM # ConvLSTM2D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import Callback



# Recuperar el corpus =======================================================================================
with gzip.open('corpus.pkl.gz', 'rb') as f:
    corpus = pickle.load(f)


fileids    = corpus.fileids()
categories = corpus.categories() 
print(categories)
print(len(categories))
print(len(fileids))


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


with gzip.open('data/X_train.pkl.gz', 'wb') as f:
    pickle.dump(X_train, f)
with gzip.open('data/X_test.pkl.gz', 'wb') as f:
    pickle.dump(X_test, f)
with gzip.open('data/y_train.pkl.gz', 'wb') as f:
    pickle.dump(y_train, f)
with gzip.open('data/y_test.pkl.gz', 'wb') as f:
    pickle.dump(y_test, f)



# Procesamiento de texto ====================================================================================
labels = LabelEncoder()
y_train_encoded = labels.fit_transform(y_train) # Labels numéricos
y_test_encoded = labels.transform(y_test)       # Labels numéricos
orig_labels = labels.inverse_transform(np.unique(y_test_encoded)) # Labels categ

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
        Embedding(vocab_size, 128),
        Bidirectional(LSTM(64, return_sequences=True)),
        Bidirectional(LSTM(64)),
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

class myCallback(Callback):
    def on_epoch_end(self, epoch, logs={}):
        if ( (logs.get('loss')<0.005) or (logs.get('accuracy')>0.999) ):
            self.model.stop_training = True
callbacks = myCallback()

results = model.fit(
    X_train, np.array(y_train_encoded),
    epochs=30,
    verbose=1,
    validation_data=(X_test, np.array(y_test_encoded)),
    callbacks = [callbacks]
)

# Guardado
'''
with gzip.open('results.pkl.gz', 'wb') as f:
    pickle.dump(results, f)

model.save('model.h5')
'''

    

# Visualizaciones ============================================================================================
plt.plot(results.history['accuracy'])
plt.plot(results.history['val_accuracy'])
plt.xlabel('epochs')
plt.ylabel('accuracy')
plt.legend(['train', 'test'])
plt.title('Accuracy estimated')
plt.savefig('figures/accuracy.png', dpi=500, bbox_inches='tight')
plt.show()

plt.plot(results.history['loss'])
plt.plot(results.history['val_loss'])
plt.xlabel('epochs')
plt.ylabel('loss')
plt.legend(['train', 'test'])
plt.title('Loss estimated')
plt.savefig('figures/loss.png', dpi=500, bbox_inches='tight')
plt.show()


# Matriz de confusión
y_hat = model.predict(X_test)
y_hat = np.argmax(y_hat, axis=1)
conf = confusion_matrix(y_test_encoded, y_hat, normalize='true')

fig, ax = plt.subplots(figsize=(6,5)) 
sns.heatmap(conf, annot=True, cmap='Blues', fmt='.2f')
plt.xticks(ticks=np.arange(len(orig_labels))+0.5, labels=orig_labels, ha='center')
plt.yticks(ticks=np.arange(len(orig_labels))+0.5, labels=orig_labels, va='center')
plt.xlabel('estimated')
plt.ylabel('real')
plt.title('Confussion Matrix')
plt.savefig('figures/confussion_matrix.png', dpi=500, bbox_inches='tight')
plt.show()


'''
# Curva ROC -> One-vs-All
num_classes = len(categories)
fpr = dict(); tpr = dict(); roc_auc = dict()

for i in range(num_classes):
    y_true = (y_test_encoded == i).astype(int)
    y_pred = (y_hat == i).astype(int)
    fpr[i], tpr[i], _ = roc_curve(y_true, y_pred)
    roc_auc[i] = auc(fpr[i], tpr[i])

plt.figure()
for i in range(num_classes):
    plt.plot(
        fpr[i],
        tpr[i],
        lw=2,
        label='{0} (AUC = {1:.2f})'.format(orig_labels[i], roc_auc[i])
    )

plt.plot([0, 1], [0, 1], color='black', lw=1, linestyle='--')
plt.xlim([0, 1])
plt.ylim([0, 1.05])
plt.xlabel('false positive rate')
plt.ylabel('true positive ratio')
plt.title('ROC One-vs-All Curve')
plt.legend(loc='lower right', fontsize=9)
plt.savefig('figures/roc.png', dpi=500, bbox_inches='tight')
plt.show()
'''