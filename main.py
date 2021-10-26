import PyQt5.QtWidgets as qw
from gui import MainWindow

WINDOW_SIZE = (1050, 700)

if __name__ == '__main__':
    app = qw.QApplication([])
    main_window = MainWindow()
    main_window.setFixedWidth(WINDOW_SIZE[0])
    main_window.setFixedHeight(WINDOW_SIZE[1])
    main_window.show()
    app.exec_()
