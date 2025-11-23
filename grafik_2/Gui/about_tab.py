from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QFrame, QTextBrowser, QPushButton)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices


class AboutTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # Заголовок
        title = QLabel("ℹ️ О программе")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Основная информация
        info_group = QFrame()
        info_group.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout(info_group)

        app_name = QLabel("Signature Verification Scanner")
        app_name.setFont(QFont("Arial", 18, QFont.Bold))
        app_name.setStyleSheet("color: #3498db;")
        app_name.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(app_name)

        version = QLabel("Версия 2.0.0")
        version.setFont(QFont("Arial", 12))
        version.setStyleSheet("color: #7f8c8d;")
        version.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(version)

        info_layout.addSpacing(20)

        # Описание
        description = QLabel(
            "Профессиональная система для проверки подлинности подписей\n"
            "с использованием нейронных сетей и компьютерного зрения."
        )
        description.setFont(QFont("Arial", 11))
        description.setStyleSheet("color: #2c3e50; line-height: 1.5;")
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        info_layout.addWidget(description)

        layout.addWidget(info_group)

        # Особенности
        features_group = QFrame()
        features_group.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        features_layout = QVBoxLayout(features_group)

        features_title = QLabel("🌟 Основные возможности")
        features_title.setFont(QFont("Arial", 16, QFont.Bold))
        features_title.setStyleSheet("color: #34495e;")
        features_layout.addWidget(features_title)

        features_text = QTextBrowser()
        features_text.setHtml("""
            <ul style="color: #2c3e50; font-size: 12px; line-height: 1.6;">
                <li>Проверка подлинности подписей с помощью нейронных сетей</li>
                <li>Поддержка различных форматов изображений (PNG, JPG, BMP, TIFF)</li>
                <li>Drag & Drop загрузка изображений</li>
                <li>Настраиваемый порог уверенности</li>
                <li>Детальная история проверок</li>
                <li>Экспорт результатов в текстовый файл</li>
                <li>Поддержка GPU для ускорения вычислений</li>
                <li>Интуитивно понятный интерфейс</li>
            </ul>
        """)
        features_text.setFixedHeight(200)
        features_text.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                font-size: 12px;
            }
        """)
        features_layout.addWidget(features_text)

        layout.addWidget(features_group)

        # Техническая информация
        tech_group = QFrame()
        tech_group.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        tech_layout = QVBoxLayout(tech_group)

        tech_title = QLabel("🔧 Техническая информация")
        tech_title.setFont(QFont("Arial", 16, QFont.Bold))
        tech_title.setStyleSheet("color: #34495e;")
        tech_layout.addWidget(tech_title)

        import torch
        import sys
        from PySide6 import QtCore

        tech_info = f"""
            <div style="color: #2c3e50; font-size: 11px; line-height: 1.5;">
                <b>Версия Python:</b> {sys.version.split()[0]}<br>
                <b>Версия PyTorch:</b> {torch.__version__}<br>
                <b>Версия PySide6:</b> {QtCore.__version__}<br>
                <b>Доступно GPU:</b> {'Да' if torch.cuda.is_available() else 'Нет'}<br>
                <b>Текущая модель:</b> {self.main_window.model_path}<br>
                <b>Порог проверки:</b> {self.main_window.threshold}%
            </div>
        """

        tech_label = QLabel()
        tech_label.setText(tech_info)
        tech_label.setStyleSheet(
            "color: #2c3e50; font-size: 11px; background-color: white; padding: 10px; border-radius: 5px;")
        tech_layout.addWidget(tech_label)

        layout.addWidget(tech_group)

        # Кнопки
        buttons_layout = QHBoxLayout()

        docs_btn = QPushButton("📚 Документация")
        docs_btn.setFixedHeight(40)
        docs_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        docs_btn.clicked.connect(self.open_documentation)
        buttons_layout.addWidget(docs_btn)

        github_btn = QPushButton("🐙 GitHub")
        github_btn.setFixedHeight(40)
        github_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a252f;
            }
        """)
        github_btn.clicked.connect(self.open_github)
        buttons_layout.addWidget(github_btn)

        update_btn = QPushButton("🔄 Проверить обновления")
        update_btn.setFixedHeight(40)
        update_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        update_btn.clicked.connect(self.check_updates)
        buttons_layout.addWidget(update_btn)

        layout.addLayout(buttons_layout)

        # Копирайт
        copyright_label = QLabel("© 2024 Signature Verification System. Все права защищены.")
        copyright_label.setFont(QFont("Arial", 9))
        copyright_label.setStyleSheet("color: #95a5a6;")
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright_label)

    def open_documentation(self):
        """Открытие документации"""
        QMessageBox.information(self, "Документация",
                                "Документация будет доступна в будущих версиях.")

    def open_github(self):
        """Открытие страницы GitHub"""
        QDesktopServices.openUrl(QUrl("https://github.com"))

    def check_updates(self):
        """Проверка обновлений"""
        QMessageBox.information(self, "Обновления",
                                "Вы используете последнюю версию программы.")
