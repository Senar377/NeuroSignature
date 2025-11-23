import sys
import os

# Добавляем путь к папке Gui в Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Gui'))

from PySide6.QtWidgets import QApplication
from Gui.main_window import MainWindow


def main():
    # Создаем приложение
    app = QApplication(sys.argv)
    app.setApplicationName("NeuroSignature")
    app.setApplicationVersion("1.0")

    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()

    # Запускаем главный цикл
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
