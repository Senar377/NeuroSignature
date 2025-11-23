from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                               QLabel, QPushButton, QComboBox, QGroupBox,
                               QTextEdit, QSplitter, QStackedWidget, QListWidget,
                               QListWidgetItem, QFileDialog, QMessageBox, QProgressBar)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QFont
import os
import sys

from Grafic.ui.scanner_widget import ScannerWidget
from Grafic.ui.history_widget import HistoryWidget


class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.current_model = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.config.get('app_name', 'NeuroSignature Scanner'))
        self.setGeometry(100, 100, *self.config.get('window_size', [1400, 800]))

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Создаем splitter для разделения областей
        splitter = QSplitter(Qt.Horizontal)

        # Левая панель - навигация
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Правая панель - содержимое
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        # Устанавливаем пропорции
        splitter.setSizes([250, 1150])

        main_layout.addWidget(splitter)

    def create_left_panel(self):
        """Создание левой панели навигации"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Заголовок
        title = QLabel("Сканер")
        title.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            margin: 15px; 
            color: #2c3e50;
            text-align: center;
        """)
        layout.addWidget(title)

        # Навигационный список
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: #f8f9fa;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-bottom: 1px solid #e9ecef;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
                border-radius: 5px;
                margin: 2px 5px;
            }
        """)

        # Добавляем пункты навигации
        nav_items = [
            "🔍 Сканирование",
            "📊 История проверок",
            "⚙️ Настройки отчета",
            "ℹ️ Инструкция"
        ]

        for item in nav_items:
            list_item = QListWidgetItem(item)
            list_item.setSizeHint(QSize(0, 50))
            self.nav_list.addItem(list_item)

        self.nav_list.currentRowChanged.connect(self.on_navigation_changed)
        layout.addWidget(self.nav_list)

        # Группа моделей
        models_group = QGroupBox("Модели")
        models_layout = QVBoxLayout()
        models_group.setLayout(models_layout)

        self.model_combo = QComboBox()
        available_models = self.config.get('model_settings', {}).get('available_models', [])
        self.model_combo.addItems(available_models)
        models_layout.addWidget(QLabel("Выбрать модель:"))
        models_layout.addWidget(self.model_combo)

        load_model_btn = QPushButton("Загрузить модель")
        load_model_btn.clicked.connect(self.load_model)
        load_model_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        models_layout.addWidget(load_model_btn)

        layout.addWidget(models_group)
        layout.addStretch()

        return panel

    def create_right_panel(self):
        """Создание правой панели с содержимым"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)

        # Stacked widget для переключения между экранами
        self.stacked_widget = QStackedWidget()

        # Экран сканирования
        self.scanner_widget = ScannerWidget(self.config)
        self.stacked_widget.addWidget(self.scanner_widget)

        # Экран истории
        self.history_widget = HistoryWidget(self.config)
        self.stacked_widget.addWidget(self.history_widget)

        # Экран настроек отчета
        self.settings_widget = self.create_settings_widget()
        self.stacked_widget.addWidget(self.settings_widget)

        # Экран инструкции
        self.instruction_widget = self.create_instruction_widget()
        self.stacked_widget.addWidget(self.instruction_widget)

        layout.addWidget(self.stacked_widget)

        return panel

    def create_settings_widget(self):
        """Создание виджета настроек отчета"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        title = QLabel("Настройки отчета")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)

        # Здесь можно добавить настройки формата отчета, параметров вывода и т.д.
        settings_text = QLabel("Настройки формата отчетов и параметров вывода будут здесь")
        settings_text.setStyleSheet("font-size: 16px; margin: 20px;")
        layout.addWidget(settings_text)

        layout.addStretch()
        return widget

    def create_instruction_widget(self):
        """Создание виджета инструкции"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        title = QLabel("ИНСТРУКЦИЯ ПОЛЬЗОВАНИЯ ПРИЛОЖЕНИЕМ")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px; text-align: center;")
        layout.addWidget(title)

        instruction_text = QTextEdit()
        instruction_text.setPlainText("""
1. ВЫБОР МОДЕЛИ
   - Выберите модель из выпадающего списка в левой панели
   - Нажмите кнопку "Загрузить модель"

2. СКАНИРОВАНИЕ ПОДПИСЕЙ
   - Перейдите в раздел "Сканирование"
   - Нажмите "Выбрать оригинальную подпись" и выберите эталонное изображение
   - Нажмите "Выбрать проверяемую подпись" и выберите изображение для проверки
   - Нажмите "Запустить проверку" для анализа

3. ПРОСМОТР РЕЗУЛЬТАТОВ
   - Результат отобразится в виде процента оригинальности
   - Зеленый цвет - подпись оригинальна
   - Красный цвет - подпись поддельная

4. ИСТОРИЯ ПРОВЕРОК
   - Все проверки сохраняются в истории
   - Можно просматривать предыдущие результаты

5. НАСТРОЙКИ
   - В разделе "Настройки отчета" можно настроить параметры вывода

ТРЕБОВАНИЯ К ИЗОБРАЖЕНИЯМ:
- Форматы: PNG, JPG, JPEG
- Рекомендуемый размер: 128x256 пикселей
- Черно-белые изображения в градациях серого
        """)
        instruction_text.setReadOnly(True)
        instruction_text.setStyleSheet("font-size: 14px; margin: 20px;")
        layout.addWidget(instruction_text)

        return widget

    def on_navigation_changed(self, index):
        """Обработчик изменения навигации"""
        self.stacked_widget.setCurrentIndex(index)

    def load_model(self):
        """Загрузка выбранной модели"""
        model_name = self.model_combo.currentText()
        try:
            # Здесь будет загрузка модели через model_loader
            QMessageBox.information(self, "Успех", f"Модель {model_name} загружена успешно!")
            self.current_model = model_name
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить модель: {str(e)}")
