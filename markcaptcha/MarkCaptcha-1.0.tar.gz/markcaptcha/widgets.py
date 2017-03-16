from os import path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, QGridLayout, \
    QHBoxLayout, QVBoxLayout, QFileDialog, QMainWindow, QDockWidget

from markcaptcha.tasks import ImageQueue


class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.te_src = QLineEdit(self)
        self.te_src.setToolTip("输入图片url或本地目录")
        self.te_dst = QLineEdit(self)
        self.te_dst.setEnabled(False)
        self.btn_ok = QPushButton("OK")
        self.btn_clear = QPushButton("Clear")
        self.btn_ok.clicked.connect(self._proceed)
        self.btn_clear.clicked.connect(self._clear)
        self.btn_select_src = QPushButton("...")
        self.btn_select_dst = QPushButton("...")
        self.btn_select_src.clicked.connect(self._select_folder(self.te_src))
        self.btn_select_dst.clicked.connect(self._select_folder(self.te_dst))

        self._init_ui()

    def _init_ui(self):
        # set layout
        main_layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        grid_layout.addWidget(QLabel("图片来源"), 1, 0)
        grid_layout.addWidget(QLabel("输出目录"), 2, 0)
        grid_layout.addWidget(self.te_src, 1, 1)
        grid_layout.addWidget(self.btn_select_src, 1, 2)
        grid_layout.addWidget(self.te_dst, 2, 1)
        grid_layout.addWidget(self.btn_select_dst, 2, 2)
        h_layout.addWidget(self.btn_clear)
        h_layout.addWidget(self.btn_ok)
        main_layout.addLayout(grid_layout)
        main_layout.addLayout(h_layout)
        self.setLayout(main_layout)
        self.setGeometry(300, 300, 400, 200)
        self.setWindowTitle("简易打码器")

    def _select_folder(self, line_edit):
        def select():
            folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
            if folder:
                line_edit.setText(folder)

        return select

    def _proceed(self):
        if not self.te_src.text().strip():
            self.te_src.setFocus()
        elif not self.te_dst.text().strip():
            self.te_dst.setFocus()
        else:
            src = self.te_src.text()
            if src.startswith('http') or path.isdir(src):
                self.wind = WorkingWindow(self.te_src.text(),
                                          self.te_dst.text())
                self.wind.show()
                self.close()
            else:
                self.te_src.selectAll()
                return

    def _clear(self):
        self.te_src.clear()
        self.te_dst.clear()


class WorkingWindow(QMainWindow):
    def __init__(self, src, dst):
        """
        打码界面
        :param src: 验证码所在目录或url
        :param dst: 验证码输出目录
        """
        super().__init__()
        self.save = 0
        self.passed = -1
        self.img_queue = ImageQueue(src, dst)
        self.setGeometry(300, 300, 400, 200)
        self.setWindowTitle("打码器")

        self.et = QLineEdit()
        self.lbl = QLabel("hello, press enter to start!")

        self.et.setAlignment(Qt.AlignCenter)
        self.et.returnPressed.connect(self._submit)
        dock = QDockWidget('输入框')
        dock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        dock.setWidget(self.et)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.lbl)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

    def _submit(self):
        # 保存
        content = self.et.text()
        if content.strip() and self.lbl.pixmap():
            self.save += 1
            self.img_queue.save(content, self.lbl.pixmap())
        else:
            self.passed += 1
        # 加载
        img = self.img_queue.get()
        if img:
            self.lbl.setPixmap(img)
        else:
            self.lbl.setText('休息一下')
        self.et.clear()
        self.statusBar().showMessage('save: %d/%s\t\tpass: %d' % (self.save, self.img_queue.total, self.passed))
