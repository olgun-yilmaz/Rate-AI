import os
import sqlite3

import pandas as pd

import requests

from bs4 import BeautifulSoup

from data_extractor.config import MOVIE_BASE_URL

resources_folder = "resources/"

if not os.path.exists(resources_folder):
    os.mkdir(resources_folder)

path = resources_folder+"movie_dataset.csv"

conn = sqlite3.connect(resources_folder + "database.db")
cursor = conn.cursor()

def create_table():
    cursor.execute("CREATE TABLE IF NOT EXISTS Movies (id TEXT UNIQUE, numComments INT)")
    conn.commit()
    try:
        cursor.execute("INSERT INTO Movies (id, numComments) VALUES (?, ?)",('StartPage',1))
        conn.commit()
    except sqlite3.IntegrityError:
        pass

def create_csv(path = path):
    if not os.path.isfile(path):
        columns = ["ratings", "comments"]
        df = pd.DataFrame(columns=columns)
        df.to_csv(path, index=False,encoding='utf-8')

create_table()
create_csv()

def add_to_database(id, numComments):
    cursor.execute("INSERT INTO Movies (id,numComments) VALUES (?,?)",(id, numComments))
    conn.commit()

def is_product_exists(id):
    cursor.execute("SELECT * FROM Movies WHERE id=?", (id,))
    data = cursor.fetchone()
    if data is None:
        return False
    return True

def save_data(movie,data,path=path): # çekilen verileri dosyaya kaydeden fonksiyon
    try:
        ratings = list()
        comments = list()
        for rating,comment in data:
            ratings.append(rating)
            comments.append(comment)

        df = pd.read_csv(path)

        row = pd.DataFrame({'ratings': ratings, 'comments': comments})

        df = pd.concat([df, row], ignore_index=True)

        df.to_csv(path, index=False)

        add_to_database(movie,len(data))

    except TypeError:
        pass

def filter_comments(ratings,comments):
    pos_counter = 0
    neg_counter = 0
    rated_comments = list()
    for rating, comment in zip(ratings, comments):
        if rating > 3:
            rating = 1

        elif rating < 3:
            rating = 0

        if rating != 3:
            if rating == 0:
                neg_counter += 1
            else:
                pos_counter += 1

            rated_comments.append((rating,comment))
    print(pos_counter,neg_counter)

    return rated_comments

def get_comments(index):
    movie = f"film-{index}"
    is_comment_exists = False

    if is_product_exists(movie):  # aynı ürünün iki kez eklenmesi engelleniyor.
        print("\nbu film zaten sistemde kayıtlı.\n")
        return

    comments = list()
    ratings = list()

    end_flag = False

    url = f"https://{MOVIE_BASE_URL}{movie}/kullanici-elestirileri/"
    page_num = 1
    while not end_flag:
        if page_num != 1:
            response = requests.get(f"{url}?page={page_num}")
        else:
            response = requests.get(url)

        html_content = response.content

        soup = BeautifulSoup(html_content, "html.parser") # soup kullanılıyor.

        comment_counter, rating_counter = 0, 0

        for i in soup.find_all("div",{"class": "content-txt review-card-content"}):  # yorumu çekmek için gerekli işlemler.
            is_comment_exists = True
            comment = (i.text)
            if comment != "\n":
                comment = comment.replace("\n", "")
                if not comment in comments:
                    comments.append(comment)
                    comment_counter += 1
                else:
                    end_flag = True
        if not is_comment_exists:
            print(f"{movie} --> BULUNAMADI.")
            return

        for i in soup.find_all("span", {"class": "stareval-note"}):
            if rating_counter < comment_counter:
                try:
                    rating = round(float(i.text.replace(",", ".")))
                except ValueError:
                    rating = 0
                ratings.append(rating)
                rating_counter += 1
            else:
                break
        page_num += 1

    rated_comments = filter_comments(ratings,comments)
    save_data(movie=movie,data=rated_comments,path=path)

def update_start_page(i):
    cursor.execute("UPDATE Movies SET numComments=? WHERE id=?",(i,'StartPage'))
    conn.commit()

cursor.execute("SELECT numComments FROM Movies WHERE id = ?",('StartPage',))
first_movie = cursor.fetchone()[0]

last_movie = 328142 # vizyondaki son film.

for i in range(first_movie,last_movie+1):
    get_comments(i)
    update_start_page(i)