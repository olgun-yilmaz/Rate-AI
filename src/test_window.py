from functools import partial

from PyQt5.QtCore import QSize, QTimer, Qt, QObject
from PyQt5.QtGui import QIcon, QPixmap, QTextCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QMessageBox, QPushButton, QHBoxLayout

from src.app_module import icon_folder, customize_widget

class Enter(QObject): # enter tuşunun özelleştirilmesini sağlayan sınıf
    def __init__(self,label = None, area = None, func = None):
        super().__init__()
        area.installEventFilter(self)

        self.label = label
        self.area = area
        self.func = func

    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress:
            if event.key() in [Qt.Key_Enter, Qt.Key_Return]: # enter tuşuna basıldıysa
                self.func(self.label,self.area) # metni analiz et.
                return True

        return super().eventFilter(obj, event)


class TestWindow(QWidget):

    def __init__(self,model):
        super().__init__()
        self.timer = QTimer()
        self.model = model
        self.default_text = "YORUM YAP..."
        self.init_ui()

    def update_label(self,result_label,text):
        result_label.setText(text)
    

    def flush_area(self):
        text_area = self.sender()
        text_area.blockSignals(True)
        text_area.setPlainText("")

    def test_it(self,result_label,text_area):
        user_comment = text_area.toPlainText()

        if user_comment.strip() == str() or user_comment.strip() ==  self.default_text:
            QMessageBox.warning(self, 'Uyarı', 'Lütfen bir yargı belirtiniz.') # direkt olarak fonksiyon çağrıldıysa
        else:
            interpret = self.model.interpret_comment(user_comment) # ifadeyi yorumla
            result_label.setText("SONUÇ : ")
            # yeni bir test gerçekleşmesi durumunda kullanıcının anlaması için önce ekran temizleniiyor

            self.timer.timeout.connect(partial(self.update_label, result_label,text="SONUÇ : " + interpret))
            self.timer.start(250) # kullanıcının yeniden yorumlandığını anlayabileceği kadar süre bekle

    def init_ui(self):
        x,y = 1000,667 # pencere boyutu

        background = QLabel(self)
        background.setPixmap(QPixmap(icon_folder+"model_test_background.jpg")) # arka plan
        background.adjustSize()

        text_area = QTextEdit(self)
        customize_widget(widget=text_area,text=self.default_text,color="white",text_size=25)
        text_area.setFixedSize(x//1.05,y//2.6)
        text_area.moveCursor(QTextCursor.End)
        text_area.textChanged.connect(self.flush_area)

        area_layout = QHBoxLayout()
        area_layout.addWidget(text_area, alignment=Qt.AlignCenter)

        result_label = QLabel(self)
        customize_widget(widget=result_label, text="SONUÇ : ", color="white",text_size=28)

        self.enter = Enter(result_label,text_area,self.test_it) # event filter

        result_layout = QHBoxLayout()
        result_layout.addWidget(result_label, alignment=Qt.AlignCenter)

        send_button = QPushButton(self)
        customize_widget(widget=send_button, color="white")
        send_button.setIcon(QIcon(icon_folder+"enter.png"))
        send_button.setIconSize(QSize(100,100))
        send_button.clicked.connect(partial(self.test_it,result_label,text_area))

        button_layout = QHBoxLayout()
        button_layout.addWidget(send_button, alignment=Qt.AlignCenter)

        v_box = QVBoxLayout()

        v_box.addSpacing(120)
        v_box.addLayout(area_layout)
        v_box.addStretch()
        v_box.addLayout(result_layout)
        v_box.addLayout(button_layout)
        v_box.addSpacing(100)

        self.setLayout(v_box)
        self.setFixedSize(x,y)
        self.setWindowTitle("MODEL TEST")
        self.setWindowIcon(QIcon(icon_folder + "model_test_icon.png"))
        self.show()