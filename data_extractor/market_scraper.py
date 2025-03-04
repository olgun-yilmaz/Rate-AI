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


import sys
import os

import sqlite3

import requests

from bs4 import BeautifulSoup

from data_extractor.config import MARKET_BASE_URL

# gerekli modüller import ediliyor.

resources_folder = "resources/" # dosyanın tutulacağı klasör

if not os.path.exists(resources_folder):
    os.mkdir(resources_folder)

path = resources_folder + "market_dataset.txt" # dosya yolu

conn = sqlite3.connect(resources_folder + "database.db") # veritabanı bağlantısı kuruluyor.
cursor = conn.cursor()

def create_table(): # Tablo yoksa oluşturan fonksiyon
    cursor.execute("CREATE TABLE IF NOT EXISTS Products (name TEXT, numNegatives INT, numPositives INT, total INT, info TEXT)")
    conn.commit()

def add_to_database(name,negatives,positives,total,info): # ürün ekleme fonksiyonu
    cursor.execute("INSERT INTO Products (name,numNegatives,numPositives,total,info) VALUES (?,?,?,?,?)",
                   (name,negatives,positives,total,info))
    conn.commit()

def is_product_exists(name): # ürünün daha önce kaydedilip kaydedilmediğini denetleyen fonksiyon
    cursor.execute("SELECT * FROM Products WHERE name=?", (name,))
    data = cursor.fetchone()
    if data is None:
        return False # kayıtlı değilse False döndür.
    return True # kayıtlıysa True döndür.

def show_progress(count,max_count): # anlık ilerlemeyi ekrana yazdıran fonksiyon
    pct_complete = count / max_count # tamamlanma oranı
    message = "\r- Progress: {0:.2f}% ".format(pct_complete*100) # ekran yüzde olarak sürekli yenilenir.
    sys.stdout.write(message)
    sys.stdout.flush()

def save_data(data,path=path): # çekilen verileri dosyaya kaydeden fonksiyon
    for rating,comment in data:
        with open(path, "a", encoding="utf-8") as file:
            line = str(rating) + "," + comment # veriler virgül ile ayrılıyor.
            file.write(line + "\n") # kaydediliyor.

def get_comments_and_ratings(negative_line,positive_line,total,product): # ilgili ürün yorumlarını alan fonksiyon
    data = list()  # çekilen verileri kaydetmek için liste
    create_table() # tablo yoksa oluştur.

    if is_product_exists(product): # aynı ürünün iki kez eklenmesi engelleniyor.
        print("\nbu ürün zaten sistemde kayıtlı.\n")

    elif not (total >= positive_line >= negative_line): # kaydetme kurallarına aykırı giriş denetleniyor.
        print("lütfen girdiğiniz paremetreleri kontrol edin.")

    else:
        page_num = 1 # ilk sayfadan başla
        while page_num <= total: # son sayfaya kadar
            if positive_line > page_num > negative_line: # 3 yıldızlı yorumlar dataset'e dahil edilmiyor. --> kararsızlar
                pass
            else:
                if page_num <= negative_line: # 1 - 2 yıldız
                    rating = 0 # olumsuz
                else: # 4 - 5 yıldız
                    rating = 1 # olumlu

                url = f"https://{MARKET_BASE_URL}{product}/?o=lowest_rating&sayfa={page_num}" # site url'i

                response = requests.get(url)

                html_content = response.content

                soup = BeautifulSoup(html_content, "html.parser") # soup kullanılıyor.

                for i in soup.find_all("div", {"class": "panel-body"}): # yorumu çekmek için gerekli işlemler.
                    comment = str(i.text.rsplit("\n")) # boş satırları sil.
                    comment = comment.rsplit()

                    start_index = comment.index("değerlendirirsin?',") + 2
                    end_index = comment.index("'\\xa0") - 8 # sitenin kaydetme şekline göre veri alma işlemleri

                    comment = comment[start_index:end_index] # yorum alınıyor.
                    comment = " ".join(comment) # string'e dönüştürülüyor.

                    comment = comment.strip("',") # string temizleme

                    data.append((rating,comment)) # rating ve comment listeye tuple olarak ekleniyor.

                show_progress(count=page_num,max_count=total) # ilerlemeyi görebilmek için.

            page_num += 1 # sayfaları gez.

        save_data(data, path)  # sadece tüm veriler başarıyla çekildiyse dosyaya kaydediyor.
        # böylece kaydederken bağlantı hatası olması halinde aynı verilerin tekrarlanması önleniyor.

        num_negatives = negative_line # olumsuz yorum sayısı
        num_positives = total - positive_line # olumlu yorum sayısı
        num_total = num_negatives + num_positives # toplam yorum sayısı
        info = str(negative_line) + "---" + str(positive_line) + "---" + str(total) # parametre bilgileri

        add_to_database(name=product, negatives = num_negatives,
                        positives = num_positives, total = num_total,
                        info = info)
        # kaydetme işlemi tamamlandıktan sonra tabloya ekle.


# örnek bir veri çekme işlemi :
get_comments_and_ratings(15,985,1000,
                         "la-roche-posay-anthelios-uvmune400-oil-control-gel")