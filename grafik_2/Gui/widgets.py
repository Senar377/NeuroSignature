from PySide6.QtWidgets import QLabel, QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap


class DragDropLabel(QLabel):
    image_dropped = Signal(str)

    def __init__(self, text="Перетащите изображение сюда", parent=None):
        super().__init__(text, parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #555555;
                border-radius: 10px;
                padding: 20px;
                background-color: #1e1e1e;
                color: #cccccc;
                font-size: 14px;
                qproperty-alignment: AlignCenter;
            }
            QLabel:hover {
                border-color: #0078d7;
                background-color: #2a2a2a;
                color: #ffffff;
            }
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                event.acceptProposedAction()
                self.setStyleSheet("""
                    QLabel {
                        border: 2px dashed #0078d7;
                        border-radius: 10px;
                        padding: 20px;
                        background-color: #2a2a2a;
                        color: #ffffff;
                        font-size: 14px;
                    }
                """)

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #555555;
                border-radius: 10px;
                padding: 20px;
                background-color: #1e1e1e;
                color: #cccccc;
                font-size: 14px;
            }
            QLabel:hover {
                border-color: #0078d7;
                background-color: #2a2a2a;
                color: #ffffff;
            }
        """)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #555555;
                border-radius: 10px;
                padding: 20px;
                background-color: #1e1e1e;
                color: #cccccc;
                font-size: 14px;
            }
            QLabel:hover {
                border-color: #0078d7;
                background-color: #2a2a2a;
                color: #ffffff;
            }
        """)

        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                    self.image_dropped.emit(file_path)
                    event.accept()
                    return

            QMessageBox.warning(self, "Ошибка", "Файл не является изображением")
        event.ignore()

    def set_image(self, file_path):
        """Установка изображения в label"""
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            self.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.setText("")
        else:
            self.setText("Не удалось загрузить изображение")

    def clear_image(self):
        """Очистка изображения"""
        self.clear()
        self.setText("Перетащите изображение сюда")
