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

# PROJENİN FARKLI BÖLÜMLERİNDE ORTAK OLARAK KULLANILAN DEĞİŞKEN VE FONKSİYONLARIN BULUNDUĞU DOSYA

import sqlite3

from PyQt5.QtWidgets import QPushButton

# gerekli modüller import ediliyor.

icon_folder = "app_icons/" # iconların bulunduğu klasör

resources_folder = "src/resources/" # kaynak dosyalarının bulunduğu klasör

conn = sqlite3.connect(resources_folder+"database.db") # bağlantı kur.
cursor = conn.cursor()

# style sheet fonksiyonu
get_features = lambda font="Kantumruy", size=17, color="black",background_color="transparent",\
                      border=0,border_color="black":("font-family: {}; font-size: {}px; color: {};background-color: {};border: {}px solid {};"
     .format(font, size, color, background_color,border,border_color))


def set_checkbox_icon(checkbox,path,x=100,y=100): # check_box icon için fonksiyon
    checkbox.setStyleSheet(f'''
        QCheckBox::indicator {{
            width: {x}px;
            height: {y}px;
            border-image: url({path});
        }}
    ''')

class RoundButton(QPushButton): # özelleştirilmiş buton
    def __init__(self,x=250,y=60,text="Go"):
        super().__init__()
        #border-radius: {y//2}px;
        self.setFixedSize(x,y)
        self.setText(text)
        self.setStyleSheet(f"""
    QPushButton {{
        background-color: grey;
        color: black;
        font-family: {"Kantumruy"};
        font-size: {30}px;
        
    }}
    QPushButton:hover {{
        background-color: #45a049;
        color : white;
    }}
""")


# widget özelleştirme
def customize_widget(widget, text_size = 40, background_color = "transparent",
                     color = "black",border_color = "black", border = 0, text="", font = "Kantumruy"):
    widget.adjustSize()
    widget.setStyleSheet(
            get_features(size=text_size, background_color=background_color, color=color,
                         border=border, border_color=border_color,font=font))
    widget.setText(text)

# pencerelerde göstermek için dosya ismini sadeleştiriyor.
def get_file_name(path):
    last_index = path.rfind("/") # son '/' karakteri
    filename = path[last_index+1:-4] # dosya uzantısı çıkarılıyor.
    return filename
    # örneğin : C:Users/Desktop/....resources/comments.txt --> ismi : comments olarak döndürür.