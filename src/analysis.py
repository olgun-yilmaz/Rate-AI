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

import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QDialog, QProgressBar, QMessageBox, QPushButton

from src.app_module import get_features, icon_folder, customize_widget, cursor, conn, get_file_name


# gerekli modüller import ediliyor.

class Analysis(QDialog): # Yüzde olarak memnuniyet oranını gösteren sınıf

    def __init__(self,rating,path,is_exists): # rating,dosya ismi ve daha önce kaydedlilip kaydedilmediği
                                              # bilgisi parametre olarak alınıyor.
        super().__init__()
        self.save_score(path,rating,is_exists)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint) # soru işareti gizleniyor.

        self.path = path
        self.file_name = get_file_name(path) # pencere ismi için dosya adı kullanılıyor.
        self.color = "transparent" # duygu durumuna göre değişken bar çubuğu rengi
        self.rating = int (rating * 100) # rating yüzde cinsinden ifade edilecek.

        self.init_ui()

    def save_score(self,path,rating,is_exists):
        if not is_exists: # kayıt yoksa
            cursor.execute("INSERT INTO Analysis VALUES (?,?)",(path,rating))
            conn.commit()

    def delete_record(self):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Onay Penceresi")
        seperator = "\n"+"*"*75+"\n"

        msgBox.setText(f"{self.file_name.upper()} ile ilgili tüm kayıtları silmek istediğinizden emin misiniz?"
                       f"{seperator}-Analiz ve puanlama işlemlerine ait tüm veriler silinecektir-{seperator}" )

        yes_button = msgBox.addButton('Evet', QMessageBox.YesRole)
        no_button = msgBox.addButton('Hayır', QMessageBox.NoRole)

        msgBox.setDefaultButton(no_button)

        msgBox.exec_()

        if msgBox.clickedButton() == yes_button: # tüm verileri temizleme işlemi
            rated_path = self.path[ : -4] + "_rated.csv"
            cursor.execute("DELETE FROM CurrentPages WHERE path=?", (rated_path,))
            conn.commit()

            cursor.execute("DELETE FROM Analysis WHERE path=?", (self.path,))
            conn.commit()

            if os.path.isfile(self.path):
                os.remove(rated_path)
            QMessageBox.information(self,"KAYIT SİLME",f"{self.file_name} ile ilgili tüm kayıtlar başarıyla silindi!")
            self.close()

    def create_delete_button(self):
        delete_button = QPushButton(self)
        delete_button.clicked.connect(self.delete_record)
        customize_widget(delete_button, text="KAYDI SİL", color="white", border_color="white",
                         border=2, background_color="transparent", text_size=20)

        delete_layout = QHBoxLayout()
        delete_layout.addWidget(delete_button, alignment=Qt.AlignCenter)

        return delete_layout

    def get_emotion(self): # ratinge göre duygu durunu döndüren fonksiyon
        if self.rating >= 75:
            emotion =  "very_happy" # icon ismi
            self.color = "#93C572" # fıstık yeşili

        elif self.rating > 60: # rating
            emotion = "happy"
            self.color = "blue"

        elif 0.25 < self.rating < 40:
            emotion = "sad"
            self.color = "orange"

        elif self.rating <= 25:
            emotion = "very_sad"
            self.color = "red"

        else:
            emotion = "confused"
            self.color = "yellow"

        return emotion # icon ismi döndürülüyor.

    def init_ui(self):
        x,y = 437,250
        right_side = QVBoxLayout() # ekranın sağı
        left_side = QVBoxLayout() # ekranın solu

        background = QLabel(self)
        background.setPixmap(QPixmap(icon_folder+"analysis_background.jpg")) # arka plan
        background.adjustSize()

        emotion = self.get_emotion() # duygu durumu tespiti - icon ismi

        progress_bar = QProgressBar(self) # Yüzdeyi gösterecek olan bar
        progress_bar.setValue(self.rating)
        progress_bar.setTextVisible(False)
        progress_bar.setFixedWidth(x//2)
        progress_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {self.color}; }}")

        emotion_label = QLabel(self) # ilgili duyguyu gösteren icon
        emotion_label.setPixmap(QPixmap(icon_folder+emotion+".png"))

        progress_label = QLabel(self) # yüzdeyi sayı cinsinden ifade eden label
        customize_widget(widget = progress_label, text = f"%{self.rating}", text_size = 35, color = "white")


        left_side.addStretch()
        left_side.addWidget(progress_bar)
        left_side.addWidget(progress_label,alignment=Qt.AlignCenter) # 1600-1200

        emotion_layout = QHBoxLayout()

        emotion_layout.addSpacing(x//1.6)
        emotion_layout.addWidget(emotion_label)

        right_side.addLayout(emotion_layout)
        right_side.addStretch()

        layout = QVBoxLayout()

        delete_layout = self.create_delete_button()

        layout.addLayout(left_side)
        layout.addLayout(right_side)
        layout.addLayout(delete_layout)

        self.setLayout(layout)
        self.setWindowTitle("analiz <-> ".upper()+self.file_name.upper()) # pencere ismi
        self.setWindowIcon(QIcon(icon_folder + "analysis_icon.png")) # pencere ikonu
        self.setFixedSize(x,y) # sabit pencere boyutu