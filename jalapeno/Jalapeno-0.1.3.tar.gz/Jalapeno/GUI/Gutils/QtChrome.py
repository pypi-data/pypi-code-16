
def Browse(listener):
    from PyQt5.QtCore import QUrl 
    from PyQt5.QtWidgets import QMainWindow,QApplication
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWebEngineWidgets import QWebEngineView

    import sys

    class MainWindow(QMainWindow):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # 设置窗口标题
            self.setWindowTitle('My Browser')
            # 设置窗口图标
            #self.setWindowIcon(QIcon('icons/penguin.png'))
            self.resize(1024,768)
            #self.showFullScreen() 
            self.show()

            # 设置浏览器
            self.browser = QWebEngineView()
            url = 'http://127.0.0.1:5588'
            # url = 'https://www.google.com'
            # 指定打开界面的 URL
            self.browser.setUrl(QUrl(url))
             # 添加浏览器到窗口中
            self.setCentralWidget(self.browser)

# 创建应用

# 显示窗口

    app = QApplication(sys.argv)
# 创建主窗口
    window = MainWindow()
    window.show()
    # 运行应用，并监听事件
    app.exec_()
