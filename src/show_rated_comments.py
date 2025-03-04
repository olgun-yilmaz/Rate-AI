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

import pandas as pd

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QDialog

from src.app_module import icon_folder, get_features, cursor, conn

# gerekli modüller import ediliyor.


class ShowRatings(QDialog): # puanlanmış yorumları gösteren pencere
    def __init__(self,rated_path):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.path = rated_path
        self.num_showing_comment = 9 # bir sayfada gösterilecek yorum sayısı
        self.font_size = 90 // self.num_showing_comment + 10 
        # yazı boyutu da sayfadaki yorum sayısına göre ayarlanıyor.

        self.current_window_index, self.num_comment = int(), int() # bulunulan sayfa ve toplam yorum sayısı

        self.layout = QVBoxLayout()

        self.comment_list, self.rating_list = list(), list() # yorum-rating listeleri

        self.get_active_window_index() # son bakılan pencrenin indeksini getir.

        self.init_ui()


    def create_new_star(self):
        star = QLabel(self)
        star.setStyleSheet(get_features(background_color="transparent"))
        return star

    def is_file_exists(self): # dosya ismi veritabanında kayıtlı mı?
        cursor.execute("SELECT * FROM CurrentPages WHERE path = ?", (self.path,))
        data = cursor.fetchone()
        if data is None:
            return False # değil
        return True # kayıtlı

    def find_the_last_page(self):
        if self.num_comment == 0: # hiç yorum yoksa
            return 1  # sadece birinci sayfa
        elif self.num_comment % self.num_showing_comment == 0: # tam bölünüyorsa
            return int(self.num_comment / self.num_showing_comment)
        else: # tam bölünmüyorsa
            return int(self.num_comment // self.num_showing_comment) + 1

    def get_active_window_index(self): # kullanıcın en son hangi  sayfada kaldığı bilgisi
        try:
            cursor.execute("SELECT currentPage FROM CurrentPages WHERE path=?", (self.path,))

            self.current_window_index = cursor.fetchone()[0]
        except TypeError: # daha önce harhangi bir sayfa değiştirme işlemi yapılmadıysa
            self.current_window_index = 1

    def save_current_page(self):
        if self.is_file_exists(): # kayıt varsa güncelle
            cursor.execute("UPDATE currentPages set CurrentPage = ? WHERE path=?",
                                (self.current_window_index,self.path))

        else: # yoksa kayıt oluştur
            cursor.execute("INSERT INTO CurrentPages (path,currentPage) VALUES (?,?)",
                                    (self.path,self.current_window_index))
        conn.commit()

    def restart(self): # pencereyi yeniden başlat
        self.close()
        show_ratings = ShowRatings(self.path)
        show_ratings.exec_()

    def change_window(self): # sayfayı değiştir
        button = self.sender()
        is_changed = False
        if button.objectName() == "prev" and self.current_window_index > 1: # önceki sayfaya git
            self.current_window_index -= 1 
            is_changed = True

        elif button.objectName() == "next" and self.current_window_index < self.find_the_last_page():
            self.current_window_index += 1 # sonraki sayfaya git
            is_changed = True

        if is_changed: # ilk sayfada geri ve son sayfada ileriye basılma durumlarında yenileme yapma.
            self.save_current_page()
            self.restart()


    def get_range(self):
        df = pd.read_csv(self.path, encoding='utf-8-sig')
        comments , ratings = df["comment"] , df["rating"]

        self.num_comment = len(df) #toplam yorum sayısı

        start_index = (self.current_window_index - 1) * self.num_showing_comment
        # bir sayfadaki yorum sayısı * (pencere-1)
        end_index = start_index + self.num_showing_comment
        # başlangıç indeksi + bir sayfadaki yorum sayısı
        # örneğin sayfa 2 için --> başangıç = 1*12 = 12 ve bitiş = 12+12 = 24
        # yani ikinci sayfa 12-23 arası yorumları gösterecek.

        for i in range(self.num_comment):
            comment = comments[i]

            if  end_index > i >= start_index and not comment in self.comment_list: # tekrarlama durumu
                self.comment_list.append(str(comment))
                self.rating_list.append(ratings[i]) # sadece ratingi al.
        
        return start_index


    def show_the_comments(self):
        counter = 0
        space_size = 50

        start_index = self.get_range() # başlangıç, bitiş indeksleri ör: 36,48

        self.layout.addSpacing(space_size)

        while counter < len(self.comment_list): # tüm listeyi tara.
            content_label = QLabel(self)

            comment = self.comment_list[counter] # yorum
            rating = self.rating_list[counter] # rating


            max_len = 119 # 119 karakterden uzun yorumların sonuna 3 nokta konulacak.

            if len(comment) > max_len:
                content_label.setToolTip(comment[max_len-3:]) # yorumun üstüne gelindiğinde devamı okunabilecek.
                comment = comment[:max_len-3] + "..."


            sequence_number = counter + start_index +  1 # yorumun sırası
            self.customize_widget(widget = content_label, text = f"{sequence_number}. {comment}",
                                  font_size = self.font_size) # özelleştiriliyor.

            rate_layout = QHBoxLayout() # yıldızları tutacak layout
            rate_layout.addStretch()

            for rate_counter in range(5): # rating için yıldızlar yerleştiriliyor.
                star = self.create_new_star()
                is_rated = "unrated.png" # default olarak boş yıldız

                if rating > rate_counter: # eğer ürünün puanı sayıdan büyükse
                    is_rated = "rated.png" # yıldızı boya

                star.setPixmap(QPixmap(icon_folder + is_rated))

                rate_layout.addWidget(star)

            h_box = QHBoxLayout()

            h_box.addSpacing(space_size)
            h_box.addWidget(content_label)
            h_box.addLayout(rate_layout)
            h_box.addSpacing(space_size)

            self.layout.addLayout(h_box)
            self.layout.addStretch()

            counter += 1

        self.layout.addStretch()
        self.create_navigation_items()
    
    def create_navigation_items(self):
        next_button = QPushButton(self)
        next_button.setObjectName("next")
        
        prev_button = QPushButton(self)
        prev_button.setObjectName("prev")

        page_state = f"{self.current_window_index}/{self.find_the_last_page()}" # bulunulan/toplam

        page_label = QLabel(page_state,self)
        page_label.setStyleSheet(get_features(size=self.font_size, color="white",font="Comic sans MS"))

        navigation_widgets = [prev_button, page_label, next_button]

        navigation_layout = QHBoxLayout()
        navigation_layout.addStretch()

        for widget in navigation_widgets:

            if widget.objectName() == "prev" or widget.objectName() == "next": # ileri-geri butonları için
                widget.setIcon(QIcon(icon_folder + widget.objectName() + ".png"))
                widget.setIconSize(QSize(50, 50))
                widget.clicked.connect(self.change_window)
                widget.setStyleSheet('background: transparent; border: none;')
                
            navigation_layout.addWidget(widget) # hepsini yerleştir.

        navigation_layout.addStretch()

        self.layout.addStretch()
        self.layout.addLayout(navigation_layout)

    def customize_widget(self, widget, font_size = 25, background_color = "transparent",
                         color = "white", border_color = "white", border = 0, text=""):
        if not self.font_size is None:
            font_size = self.font_size

        widget.adjustSize()
        widget.setStyleSheet(
            get_features(size=font_size, background_color=background_color, color=color,
                         border=border, border_color=border_color))
        widget.setText(text)

    def init_ui(self):
        x,y = 1600,850

        window_background = QLabel(self)
        window_background.setPixmap(QPixmap(icon_folder + "show_rating_background.jpg"))
        window_background.adjustSize()

        self.show_the_comments()

        self.setLayout(self.layout)
        self.setFixedSize(x,y)
        self.setWindowTitle("PUANLANAN YORUMLAR")
        self.setWindowIcon(QIcon(icon_folder + "comment_icon.png"))