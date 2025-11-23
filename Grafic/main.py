import sys
import os
import json
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from Grafic.ui.main_window import MainWindow


def load_config():
    """Загрузка конфигурации из JSON файла"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Конфигурационный файл не найден! Создаю default config...")
        return create_default_config()
    except json.JSONDecodeError as e:
        print(f"Ошибка чтения конфигурационного файла: {e}")
        return create_default_config()


def create_default_config():
    """Создание конфигурации по умолчанию"""
    default_config = {
        "app_name": "NeuroSignature Scanner",
        "window_size": [1400, 800],
        "default_paths": {
            "data_directory": "./Data",
            "models_directory": "./models",
            "test_directory": "./TEST",
            "output_directory": "./outputs"
        }
    }

    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=4, ensure_ascii=False)

    return default_config


def main():
    # Загрузка конфигурации
    config = load_config()

    # Создание приложения
    app = QApplication(sys.argv)
    app.setApplicationName(config.get('app_name', 'NeuroSignature Scanner'))

    # Создание главного окна
    window = MainWindow(config)
    window.show()

    # Запуск приложения
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
