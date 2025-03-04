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

from functools import partial

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog, QHBoxLayout, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer

from src.app_module import icon_folder, customize_widget

# gerekli modüller import ediliyor.

class LoadModelThread(QThread):
    def __init__(self,path):
        super().__init__()
        self.path = path
    model = pyqtSignal(object) # modeli al

    def run(self):
        from src.load_model import LoadModel
        model = LoadModel(comments_path=self.path) # modeli yükle
        self.model.emit(model)

class LoadingDialog(QDialog): # yükleniyor penceresi
    def __init__(self,path=""):
        super().__init__()
        self.success = False # yükleme tamamlandı mı?
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.num_point = 1

        self.color = "#2F2F2F" # koyu gri

        self.estimatedCompletionTime = 14000 # yaklaşık tamamlanma süresi

        self.value = 0

        self.path = path

        self.model = None

        self.initUI()

    def initUI(self):
        x,y = 500,333
        self.setWindowTitle('Model Yükleme')
        
        self.label = QLabel(self)
        customize_widget(widget=self.label,color="white",text=f"Yükleniyor {self.num_point*'.'}")

        self.progress_label = QLabel(self)
        customize_widget(widget=self.progress_label,color="white",text=f"%0")

        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.progress_label,alignment=Qt.AlignRight)
        progress_layout.addSpacing(x//5)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedSize(x//1.5,y//25)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximum(self.estimatedCompletionTime)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {self.color};
                border: 2px solid {self.color};
            }}
            QProgressBar::chunk {{
                background-color: white;
            }}
        """)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.label,alignment=Qt.AlignCenter)
        layout.addWidget(self.progress_bar,alignment=Qt.AlignCenter)
        layout.addLayout(progress_layout)
        layout.addStretch()

        self.timer = QTimer(self)
        self.timer.timeout.connect(partial(self.update_progress_bar, self.success))
        self.timer.start(500)

        self.start_loading(self.path)

        self.setLayout(layout)
        self.setFixedSize(x,y)

        self.setStyleSheet("background-color: black;")
        self.setWindowIcon(QIcon(icon_folder+"loading_icon.png"))
        self.setWindowTitle("Model Yükleniyor...")

    def start_loading(self,path):
        self.label.setText('Yükleniyor .')
        self.thread = LoadModelThread(path=self.path)
        self.thread.model.connect(self.get_model)
        self.thread.start()

    def get_model(self, model):
        self.model = model
        self.label.setText("Yükleme \nbaşarıyla\ntamamlandı.")
        self.timer.stop()
        self.progress_label.setText("%100")
        self.progress_bar.setValue(self.estimatedCompletionTime)
        QTimer.singleShot(1000,self.close) # 1 sn başarılı ekranını göster.
        self.success = True

    def update_progress_bar(self,success):
        try:
            if not success:
                self.label.setText("Yükleniyor {}".format(self.num_point * "."))

                if self.value == self.estimatedCompletionTime:
                    self.value = int(self.estimatedCompletionTime * .99)

                self.progress_bar.setValue(self.value)

                rate = (self.value/self.estimatedCompletionTime)*100
                rate = round(rate)

                if rate == int(rate):
                    rate = int(rate)

                if rate >= 99: # tahmini  süreyi geçmesi durumunda bar 99da kalsın.
                    rate = 99

                self.progress_label.setText(f"%{rate}")

                self.num_point += 1

                if self.num_point == 4: # . / .. / ... döngüsü
                    self.num_point = 1

                self.value += 500

        except AttributeError:
            pass