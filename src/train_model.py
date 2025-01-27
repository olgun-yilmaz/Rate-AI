import os.path

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding
from tensorflow.keras.optimizers import Adam
from keras.saving.save import save_model

from src.model_module import (CustomCuDNNGRU, numwords,data_test_pad,target_test, max_tokens,
                              data_train_pad, target_train, model_path)

if os.path.isfile(model_path):
    os.remove(model_path)

model = Sequential() # katmanların sırayla eklendiği model.
embedding_size = 60 # her kelimenin vektör temsili için kullanılacak boyut
# input dim : kelime haznesi, output_dim : vektör uzunluğu, input_length = pad edilmiş dizi uzunluğu
model.add(Embedding(input_dim=numwords, output_dim=embedding_size,
                    input_length=max_tokens,name="embedding-layer"))

model.add(CustomCuDNNGRU(units = 16,return_sequences=True))
model.add(CustomCuDNNGRU(units=8, return_sequences=True))
model.add(CustomCuDNNGRU(units=4))
model.add(Dense(1,activation="sigmoid")) # 1e yakınsa olumlu, 0'a yakınsa olumsuz.

optimizer = Adam(learning_rate=1e-3)

model.compile(loss="binary_crossentropy",optimizer=optimizer,metrics=["accuracy"])

model.fit(x=data_train_pad,y=target_train,epochs = 4, batch_size = 128)


save_model(model,model_path)

result = model.evaluate(data_test_pad, target_test) # 95.07