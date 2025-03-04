# MIT License
#
# Copyright (c) 2024 Olgun Yılmaz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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