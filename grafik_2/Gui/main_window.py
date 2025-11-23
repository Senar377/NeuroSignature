import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QFileDialog, QWidget, QTextEdit,
                               QMessageBox, QScrollArea, QSizePolicy, QFrame,
                               QTabWidget, QStatusBar, QMenuBar, QMenu)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QThread
from PySide6.QtGui import QFont, QColor, QPalette, QAction, QIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_menu()

    def setup_ui(self):
        self.setWindowTitle('NeuroSignature - Анализ подписей')
        self.setGeometry(100, 100, 1200, 800)

        # Установка темной темы
        self.set_dark_theme()

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Создание вкладок
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Импорт и создание вкладок
        try:
            from Gui.processing_tab import ProcessingTab
            from Gui.verification_tab import VerificationTab
            from Gui.history_tab import HistoryTab
            from Gui.settings_tab import SettingsTab

            # Создаем вкладки БЕЗ передачи пути - модель сама найдет путь
            self.processing_tab = ProcessingTab(self)
            self.verification_tab = VerificationTab(self)
            self.history_tab = HistoryTab(self)
            self.settings_tab = SettingsTab(self)

            self.tab_widget.addTab(self.processing_tab, "📊 Анализ подписи")
            self.tab_widget.addTab(self.verification_tab, "🔍 Верификация")
            self.tab_widget.addTab(self.history_tab, "📋 История")
            self.tab_widget.addTab(self.settings_tab, "⚙ Настройки")

        except ImportError as e:
            print(f"Ошибка загрузки вкладок: {e}")
            error_label = QLabel(f"Ошибка загрузки интерфейса: {e}")
            error_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(error_label)

        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Показываем статус в статус баре
        model_handler = self.processing_tab.model_handler
        if model_handler.model_path and os.path.exists(model_handler.model_path):
            model_name = os.path.basename(model_handler.model_path)
            self.status_bar.showMessage(f"✅ Модель загружена: {model_name}")
        else:
            self.status_bar.showMessage("⚠ ДЕМО-РЕЖИМ: Модель не найдена")

    def setup_menu(self):
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu('Файл')

        open_action = QAction('Открыть изображение', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню Вид
        view_menu = menubar.addMenu('Вид')

        processing_action = QAction('Анализ подписи', self)
        processing_action.setShortcut('F1')
        processing_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        view_menu.addAction(processing_action)

        verification_action = QAction('Верификация', self)
        verification_action.setShortcut('F2')
        verification_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        view_menu.addAction(verification_action)

        # Меню Помощь
        help_menu = menubar.addMenu('Помощь')

        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def set_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2b2b2b;
                margin: 0px;
                padding: 0px;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 16px;
                border: 1px solid #555555;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #505050;
                border-color: #0078d7;
            }
            QTabBar::tab:hover {
                background-color: #484848;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #505050;
                border: 1px solid #666666;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
            QPushButton:disabled {
                background-color: #353535;
                color: #888888;
            }
            QTextEdit, QListWidget, QLineEdit, QComboBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
                font-size: 12px;
            }
            QLabel {
                background-color: transparent;
                color: #ffffff;
                padding: 4px;
            }
            QScrollArea {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QFrame {
                background-color: #1e1e1e;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #1e1e1e;
                text-align: center;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
                border-radius: 3px;
            }
            QMenuBar {
                background-color: #353535;
                color: #ffffff;
                border-bottom: 1px solid #555555;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background-color: #505050;
            }
            QMenu {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QMenu::item {
                padding: 4px 16px;
            }
            QMenu::item:selected {
                background-color: #505050;
            }
            QStatusBar {
                background-color: #353535;
                color: #cccccc;
                border-top: 1px solid #555555;
            }
            QGroupBox {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение подписи",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)"
        )
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        """Загрузка изображения в текущую вкладку"""
        current_tab = self.tab_widget.currentWidget()
        if hasattr(current_tab, 'load_image'):
            current_tab.load_image(file_path)
        elif hasattr(current_tab, 'load_reference_image'):
            # Если это вкладка верификации, загружаем как эталон
            current_tab.load_reference_image(file_path)
        else:
            # Переключаемся на вкладку анализа
            self.tab_widget.setCurrentWidget(self.processing_tab)
            self.processing_tab.load_image(file_path)

    def show_about(self):
        about_text = """
NeuroSignature - Система анализа и верификации подписей

Версия 1.0

Возможности:
• Анализ качества и характеристик подписей
• Верификация подлинности подписей
• Сравнение двух подписей на схожесть
• Ведение истории обработки

Используемые технологии:
• PySide6 для интерфейса
• PyTorch для нейросетевых моделей
• Компьютерное зрение для анализа изображений

Разработано для автоматизации проверки подписей.
"""
        QMessageBox.about(self, "О программе", about_text)

    def update_status(self, message):
        self.status_bar.showMessage(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
