import pandas as pd

from tensorflow.keras.models import load_model
from src.model_module import target_test, CustomCuDNNGRU, tokenizer, max_tokens, data_test_pad, model_path
from tensorflow.keras.preprocessing.sequence import pad_sequences


# gerekli modüller import ediliyor.

class LoadModel:  # modeli yükleyen sınıf
    def __init__(self, comments_path=str()):
        self.comments_path = comments_path  # model hangi dosya üzerinde işlem yapacak?
        self.load_model()

    def load_model(self):  # modeli yükleyen fonksiyon
        self.model = load_model(model_path, custom_objects={'CustomCuDNNGRU': CustomCuDNNGRU})

    def get_accuracy(self):  # model doğruluğu
        result = self.model.evaluate(data_test_pad, target_test)

    def convert_ratings(self,ratings):  # 0 - 1 arasındaki ratingleri
        rating_list = list()
        for i,rating in enumerate(ratings):
            rating = rating[0] # liste halinde döndüğü için
            stars = 1 + round(rating / 0.25)  # 1-5 arasında dönüştür.
            rating_list.append(stars)  # cümlelerin sonuna yaz.
        return rating_list

    def rate_the_comments(self):
        rated_comments_path = self.comments_path[:- 4] + "_rated.csv"  # yorumların puanlanıp tekrar kaydedildiği doysa
        comment_list = self.get_comments()  # tüm yorumlar alınıyor.

        tokens = tokenizer.texts_to_sequences(comment_list)  # yorumları tokenize et.
        tokens_pad = pad_sequences(tokens, maxlen = max_tokens)  # max_tokens'a göre

        ratings = self.model.predict(tokens_pad)  # tüm yorumlar için 0-1 arası ratingler

        ratings = self.convert_ratings(ratings)  # puanları 1-5 skalasında normalize et.

        data = {"comment": comment_list, "rating": ratings}

        columns = ["comment","rating"]

        df = pd.DataFrame(data, columns=columns)

        df.to_csv(rated_comments_path, index = False, encoding='utf-8-sig')


    def interpret_rating(self, rating):  # ratingleri türkçe olarak ifade et.
        statement = "OLUMLU"
        if rating < 0.5:
            statement = "OLUMSUZ"

        if rating <= 0.2 or rating >= 0.8:
            return " --> KESİNLİKLE " + statement
        elif rating <= 0.35 or rating >= 0.65:
            return " --> " + statement
        elif rating <= 0.45 or rating >= 0.55:
            return " --> EMİN DEĞİLİM AMA " + statement + " GİBİ GÖZÜKÜYOR"
        else:
            return " --> KARAR VEREMEDİM :|"

    def get_comments(self):
        comment_list = list()

        with open(self.comments_path, "r", encoding="utf-8") as file:
            content = file.readlines()
        for line in content:
            comment = line.strip("\n")
            comment_list.append(comment)

        return comment_list  # yorumları döndür.

    def interpret_comment(self, comment): # yorumla
        tokens = tokenizer.texts_to_sequences([comment])
        tokens_pad = pad_sequences(tokens, maxlen=max_tokens)

        rating = self.model.predict(tokens_pad)[0][0]
        interpret = self.interpret_rating(rating)

        return interpret  # yorumu döndür.

    def get_binary_ratings(self):
        binary_rating_list = list()
        comment_list = self.get_comments()

        tokens = tokenizer.texts_to_sequences(comment_list)
        tokens_pad = pad_sequences(tokens, maxlen=max_tokens)

        ratings = self.model.predict(tokens_pad)

        for i in range(len(comment_list)):
            rate = ratings[i][0]
            if rate > 0.5:
                binary_rate = 1  # 1e yakınsa olumlu
            else:
                binary_rate = 0  # 0a yakınsa olumsuz

            binary_rating_list.append(binary_rate)
        return binary_rating_list