# Gui/widgets.py
from PySide6.QtWidgets import QLabel, QMessageBox, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap


class DragDropLabel(QLabel):
    image_dropped = Signal(str)

    def __init__(self, text="Перетащите изображение сюда", parent=None):
        super().__init__(text, parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(300, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.current_image_path = None
        self.current_theme = "light"
        self.update_style()

    def update_style(self):
        """Обновление стиля в зависимости от темы"""
        if self.current_theme == "dark":
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
        else:
            self.setStyleSheet("""
                QLabel {
                    border: 2px dashed #cccccc;
                    border-radius: 10px;
                    padding: 20px;
                    background-color: #ffffff;
                    color: #666666;
                    font-size: 14px;
                    qproperty-alignment: AlignCenter;
                }
                QLabel:hover {
                    border-color: #0078d7;
                    background-color: #f0f0f0;
                    color: #333333;
                }
            """)

    def set_theme(self, theme):
        """Установка темы"""
        self.current_theme = theme
        self.update_style()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and self.is_image_file(urls[0].toLocalFile()):
                event.acceptProposedAction()
                self.set_highlight_style(True)

    def dragLeaveEvent(self, event):
        self.set_highlight_style(False)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.set_highlight_style(False)

        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if self.is_image_file(file_path):
                    self.image_dropped.emit(file_path)
                    event.accept()
                    return

            QMessageBox.warning(self, "Ошибка", "Файл не является изображением")
        event.ignore()

    def set_highlight_style(self, highlighted):
        """Установка стиля при наведении"""
        if highlighted:
            if self.current_theme == "dark":
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
            else:
                self.setStyleSheet("""
                    QLabel {
                        border: 2px dashed #0078d7;
                        border-radius: 10px;
                        padding: 20px;
                        background-color: #f0f0f0;
                        color: #333333;
                        font-size: 14px;
                    }
                """)
        else:
            self.update_style()

    def is_image_file(self, file_path):
        """Проверка, является ли файл изображением"""
        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif', '.webp')
        return file_path.lower().endswith(image_extensions)

    def set_image(self, file_path):
        """Установка изображения с масштабированием"""
        self.current_image_path = file_path
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            widget_size = self.size()
            scaled_pixmap = pixmap.scaled(
                max(1, widget_size.width() - 20),
                max(1, widget_size.height() - 20),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
            self.setText("")
        else:
            self.setText("Не удалось загрузить изображение")

    def clear_image(self):
        """Очистка изображения"""
        self.current_image_path = None
        self.clear()
        self.setText("Перетащите изображение сюда")

    def resizeEvent(self, event):
        """Обновление изображения при изменении размера"""
        super().resizeEvent(event)
        if self.current_image_path:
            self.set_image(self.current_image_path)