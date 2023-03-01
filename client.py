import os
import sys
from time import sleep
from socket import *
from moviepy.editor import AudioFileClip
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDesktopWidget
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QPushButton, QSlider, QLabel, QLineEdit, QTextBrowser
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QSlider

default_host = 'localhost'
default_port = '19608'
tmp_file_name = './tmp_sound.mp3'

class ChatBot(QMainWindow):
    serv_sock = socket(AF_INET, SOCK_STREAM)

    class Receiver(QThread):
        def run(self):
            while(True):
                msg = self.app.serv_sock.recv(1024)
                msg = msg.decode('utf-8', 'ignore')
                if(msg == '[quit]'):
                    break
                elif(msg.find('[10/10]') != -1):
                    self.app.help_button.setEnabled(True)
                    self.app.open_file_button.setEnabled(True)
                    self.app.disconnect_button.setEnabled(True)
                    self.app.statusBar().showMessage('Connected')
                elif(msg == ''):
                    continue
                self.app.chat_box.append(msg)
                sleep(0.3)
            self.app.serv_sock.close()
            self.app.serv_sock = socket(AF_INET, SOCK_STREAM)

        def __init__(self, app):
            super().__init__()
            self.app = app

    def convert_to_wav(self, file_name):
        AudioFileClip(file_name).write_audiofile(tmp_file_name)
        self.chat_box.append('[2/10] Sending File To Server...')
        with open(tmp_file_name, 'rb') as f:
            self.serv_sock.sendall('[Start]'.encode())
            buf = f.read(1024)
            while(buf):
                self.serv_sock.sendall(buf)
                buf = f.read(1024)
            self.serv_sock.sendall('[End]'.encode())
        os.remove(tmp_file_name)
        sleep(0.3)

    def change_summary_slider(self, value):
        self.summary_value.setText(str(value))

    def help(self):
        self.chat_box.append('[Help] 동영상을 요약해주는 챗봇입니다.')
        self.chat_box.append('[Help] Host, Port를 입력 후 Connect 버튼을 눌러주세요.')
        self.chat_box.append('[Help] 위 슬라이더를 통해 몇 줄의 문장으로 요약할지 선택하세요.')
        self.chat_box.append('[Help] 아래 Open file 버튼을 통해 동영상을 업로드해주세요.')

    def open_file(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file', './', 'Video Files (*.mp4 *.flv *.ts *.mts *.avi *.mov)')
        if(file_name[0]):
            self.chat_box.clear()
            self.chat_box.append('[1/10] Converting Video To Audio...')

            self.help_button.setEnabled(False)
            self.open_file_button.setEnabled(False)
            self.disconnect_button.setEnabled(False)
            self.statusBar().showMessage('Waiting')

            self.convert_to_wav(file_name[0])
            sleep(0.3)
            self.serv_sock.sendall(self.summary_value.text().encode())

    def connect_server(self):
        try:
            self.serv_sock.connect((self.host.text(), int(self.port.text())))
            self.__connected()
            self.chat_box.clear()
            self.chat_box.append(self.serv_sock.recv(1024).decode())
            self.recv_thread = self.Receiver(self)
            self.recv_thread.start()
        except Exception as e:
            print(e)
            self.serv_sock = socket(AF_INET, SOCK_STREAM)
            self.chat_box.append('[Error] 서버 연결을 실패했습니다.')

    def disconnect_server(self):
        self.serv_sock.sendall('[quit]'.encode())
        self.__disconnected()
        self.chat_box.append('[Info] 서버와 연결을 끊었습니다.')

    def __connected(self):
        self.host.setEnabled(False)
        self.port.setEnabled(False)
        self.connect_button.setEnabled(False)
        self.open_file_button.setEnabled(True)
        self.disconnect_button.setEnabled(True)
        self.statusBar().showMessage('Connected')

    def __disconnected(self):
        self.host.setEnabled(True)
        self.port.setEnabled(True)
        self.connect_button.setEnabled(True)
        self.open_file_button.setEnabled(False)
        self.disconnect_button.setEnabled(False)
        self.statusBar().showMessage('Not connected')

    def __init__(self):
        super().__init__()
        self.__init_UI()

    def __init_UI(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.__settings())
        vbox.addLayout(self.__chat())
        res = QWidget()
        res.setLayout(vbox)
        self.setCentralWidget(res)

        self.statusBar().showMessage('Not connected')
        self.setWindowTitle('ChatBot Project')
        self.resize(400, 600)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.show()

    def __settings(self):
        settings = QGroupBox('Setting')
        vbox = QVBoxLayout()

        hbox1 = QHBoxLayout()
        host_label = QLabel('Host')
        self.host = QLineEdit(self)
        self.host.setText(default_host)
        port_label = QLabel('Port')
        self.port = QLineEdit(self)
        self.port.setText(default_port)
        self.connect_button = QPushButton('Connect', self)
        self.connect_button.clicked.connect(self.connect_server)
        hbox1.addWidget(host_label)
        hbox1.addWidget(self.host)
        hbox1.addWidget(port_label)
        hbox1.addWidget(self.port)
        hbox1.addWidget(self.connect_button)

        hbox2 = QHBoxLayout()
        self.summary_slider = QSlider(Qt.Horizontal, self)
        self.summary_slider.setRange(1, 10)
        self.summary_slider.setSingleStep(1)
        self.summary_slider.setValue(3)
        self.summary_slider.valueChanged[int].connect(self.change_summary_slider)
        self.summary_value = QLabel('3', self)
        hbox2.addWidget(self.summary_slider)
        hbox2.addWidget(self.summary_value)

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        settings.setLayout(vbox)
        return settings

    def __chat(self):
        vbox = QVBoxLayout()
        self.chat_box = QTextBrowser(self)
        self.help_button = QPushButton('Help', self)
        self.help_button.clicked.connect(self.help)
        self.open_file_button = QPushButton('Open file', self)
        self.open_file_button.setEnabled(False)
        self.open_file_button.clicked.connect(self.open_file)
        self.disconnect_button = QPushButton('Disconnect', self)
        self.disconnect_button.clicked.connect(self.disconnect_server)
        self.disconnect_button.setEnabled(False)

        hbox = QHBoxLayout()
        hbox.addWidget(self.help_button)
        hbox.addWidget(self.open_file_button)
        hbox.addWidget(self.disconnect_button)

        vbox.addWidget(self.chat_box)
        vbox.addLayout(hbox)
        return vbox

if(__name__ == '__main__'):
    app = QApplication(sys.argv)
    ex = ChatBot()
    sys.exit(app.exec_())
