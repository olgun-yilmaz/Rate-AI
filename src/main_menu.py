import os
import numpy as np
import tkinter as tk
from tkinter import filedialog

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon,QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QMessageBox, QLabel

from src.show_rated_comments import ShowRatings
from src.app_module import get_features, icon_folder, set_checkbox_icon, RoundButton, customize_widget, \
    cursor, conn
from src.analysis import Analysis

from src.loading_dialog import LoadingDialog

from src.test_window import TestWindow

# gerekli modüller import ediliyor.

class MainMenu(QWidget): # kullanıcının ilk karşılaştığı pencere

    def __init__(self):
        super().__init__()
        self.tester_model = None # test için yüklenen model
        self.create_table()
        self.init_ui()

    def go_to_analysis_page(self,rating,path,is_exists): # analiz penceresini açan fonksiyon
        analysis = Analysis(rating,path,is_exists) # pencere açılıyor.
        analysis.exec_()

    def create_table(self): # güncel pencere bilgisi ve analiz skoru için tablo yoksa oluştur.
        cursor.execute("CREATE TABLE IF NOT EXISTS Analysis (path TEXT UNIQUE, score INT)")
        conn.commit()

        cursor.execute("CREATE TABLE IF NOT EXISTS CurrentPages (path TEXT UNIQUE, currentPage INT)")
        conn.commit()

    def normalize_rating(self,calculated_rating): # 0-1 arasındaki değer
        num_star = 1 + (calculated_rating / 0.25)
        num_star = round(num_star) # 1-5 arasında değere dönüştürülüyor.
        return num_star

    def open_file(self): # dosya işlemi yapan fonksiyon
        check = self.rating_button.isChecked() or self.analysis_button.isChecked()
        # herhangi bir işlem seçildi mi?

        if check: # seçildiyse
            root = tk.Tk()
            root.withdraw()

            path = filedialog.askopenfilename() # dosyayı aç

            if not path: # dosya var mı?
                return

            rated_path = path[:-4] + "_rated.csv"

            def open_show_ratings(rated_path):
                show_ratings = ShowRatings(rated_path)  # ratingleri gösteren pencere
                show_ratings.exec_()

            def load_model():
                loader_app = LoadingDialog(path=path)  # model yükleme penceresini aç
                loader_app.exec_()

                if not loader_app.success:  # yükleme tamamlanmadan kapatılırsa
                    model = False

                model = loader_app.model  # model yüklendi.
                return model

            if self.rating_button.isChecked(): # puanlama istendiyse
                if os.path.isfile(rated_path):
                    # daha önceden puanlandıysa dosyayı yükle
                    open_show_ratings(rated_path)
                else:
                    model = load_model()
                    if model:
                        model.rate_the_comments()  # cümleler puanlanır ve kaydedilir.

                        if os.path.isfile(rated_path):  # kayıt başarılı sonuçlandıysa
                            open_show_ratings(rated_path)
                        else:
                            QMessageBox.warning(self, 'Uyarı', 'Dosya kaydedilirken bir hata oluştu.')

            if self.analysis_button.isChecked(): # sadece duygu analizi istendiyse
                cursor.execute("SELECT score FROM Analysis WHERE path = ?",(path,))
                is_exists = False
                try:
                    avr_rating = cursor.fetchone()[0]
                    is_exists = True
                except TypeError:
                    model = load_model()
                    if model:
                        data = model.get_binary_ratings()  # 0-1ler olarak cümleler analiz ediliyor.
                        data = np.array(data)
                        avr_rating = np.mean(data)  # ortalama rating bulunuyor.
                    else : return

                self.go_to_analysis_page(avr_rating,path,is_exists) # analiz penceresi açılıyor.

        else:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen önce yapmak istediğiniz işlemi seçin.')
            # herhangi bir işlem seçilmedi uyarısı.


    def test_model(self): # kullanıcıların modelin doğruluğunu test etmesi için fonksiyon
        if self.tester_model is None: # ilk defa tıklandıysa
            loader_app = LoadingDialog() # model yükleme penceresi
            loader_app.exec_()
            if not loader_app.success: # yüklenmeden kapatılma durumu
                return
            self.tester_model = loader_app.model # model

        test_window = TestWindow(self.tester_model) # test penceresi açılıyor.
        test_window.show()


    def click(self): # seçme butonlarına tıklandığında çağrılan fonksiyon
        button = self.sender()
        icon_name = button.objectName()

        if button.isChecked(): # işaretlendiyse
            icon_name = icon_name[5:] # renki icon
        else: # işaretlenmediyse
            icon_name = "dont_" + icon_name # siyah-beyaz icon

        button.setObjectName(icon_name) # nesne ismi sonraki sefer için güncelleniyor.
        path = icon_folder + icon_name + ".png" # icon yolu

        set_checkbox_icon(checkbox=button,path=path) # icon güncelleniyor.

    def create_check_box(self,icon_name): #check_box oluşturan fonksiyon
        check_box = QCheckBox(self)

        if icon_name == "dont_rate_button":
            check_box.setToolTip("Puanla") # üstüne gelindiğinde butonun bilgi vermesi sağlanıyor.
        elif icon_name == "dont_analysis_button":
            check_box.setToolTip("Analiz Et")

        path = icon_folder + icon_name + ".png"
        check_box.setObjectName(icon_name) # tıklanma durumuna göre değişmesi için nesne ismi olarak atanıyor.

        customize_widget(widget=check_box) # default olarak özelleştiriliyor.
        set_checkbox_icon(checkbox=check_box,path=path) # icon yerleştir.

        check_box.clicked.connect(self.click) # tıklanırsa fonksiyona git.

        return check_box

    def init_ui(self):
        x,y = 650,400 # pencere boyutu
        button_size = 100 # buton ikonu boyutu

        background = QLabel(self)
        background.setPixmap(QPixmap(icon_folder + "main_background.jpg")) # arka plan
        background.adjustSize()

        open_button = QPushButton(self) # dosya yükleme butonu
        open_button.setToolTip("DOSYA YÜKLE")

        open_button.setIcon(QIcon(icon_folder+"load_button.png"))
        open_button.setIconSize(QSize(button_size,button_size))
        open_button.setStyleSheet(get_features(color="white"))

        open_button.clicked.connect(self.open_file)

        self.analysis_button = self.create_check_box(icon_name="dont_analysis_button")
        self.rating_button = self.create_check_box(icon_name="dont_rate_button")
        # default olarak siyah beyaz iconlar veriliyor. --> işaretlenmemiş.

        check_box_layout = QHBoxLayout()

        check_box_layout.addStretch()
        check_box_layout.addWidget(self.analysis_button)
        check_box_layout.addStretch()
        check_box_layout.addWidget(self.rating_button)
        check_box_layout.addStretch() # yerleştirme işlemleri

        test_me_button = RoundButton(text="BENİ TEST ET!") # test butonu
        test_me_button.clicked.connect(self.test_model)

        test_layout = QHBoxLayout()
        test_layout.addWidget(test_me_button, alignment=Qt.AlignCenter)

        v_box = QVBoxLayout()

        v_box.addWidget(open_button)
        v_box.addStretch()
        v_box.addLayout(check_box_layout)
        v_box.addStretch()
        v_box.addLayout(test_layout)

        self.setLayout(v_box)
        self.setWindowTitle("RATE-AI")
        self.setFixedSize(x,y)
        self.setWindowIcon(QIcon(icon_folder + "analysis_icon.png"))
        self.show()