# Gui/settings_tab.py
import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QGroupBox, QComboBox,
    QCheckBox, QSpinBox, QDoubleSpinBox, QLineEdit,
    QFileDialog, QScrollArea, QFrame, QSlider, QFormLayout,
    QGridLayout
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QFont, QColor


class SettingsTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings = QSettings("NeuroSignature", "AppSettings")
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок
        title_label = QLabel("Настройки приложения")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #ffffff; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Scroll area для настроек
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #34495e;
                border-radius: 8px;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2c3e50;
                width: 10px;
                border-radius: 5px;
                margin: 1px;
            }
            QScrollBar::handle:vertical {
                background-color: #4a6572;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5d7b8a;
            }
        """)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(15, 15, 15, 15)

        # НАСТРОЙКИ ИНТЕРФЕЙСА
        interface_group = self.setup_interface_settings()
        scroll_layout.addWidget(interface_group)

        # Настройки модели
        model_group = self.setup_model_settings()
        scroll_layout.addWidget(model_group)

        # Настройки UI
        ui_group = self.setup_ui_settings()
        scroll_layout.addWidget(ui_group)

        # Кнопка "Применить" - НОВАЯ КНОПКА
        apply_frame = QFrame()
        apply_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 8px;
                padding: 15px;
                margin-top: 20px;
                margin-bottom: 10px;
            }
        """)
        apply_layout = QVBoxLayout(apply_frame)

        # Кнопка "Применить настройки"
        self.apply_btn = QPushButton("✅ Применить настройки интерфейса")
        self.apply_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.apply_btn.setFixedHeight(45)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
                border-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #229954;
                border-color: #1e8449;
            }
        """)
        self.apply_btn.clicked.connect(self.apply_interface_settings)

        # Описание
        apply_desc = QLabel(
            "Эта кнопка применяет только настройки интерфейса.\nНастройки модели требуют сохранения через основную кнопку 'Сохранить'.")
        apply_desc.setFont(QFont("Arial", 9))
        apply_desc.setStyleSheet("color: #bdc3c7; text-align: center; padding: 5px;")
        apply_desc.setAlignment(Qt.AlignCenter)
        apply_desc.setWordWrap(True)

        apply_layout.addWidget(self.apply_btn)
        apply_layout.addWidget(apply_desc)
        scroll_layout.addWidget(apply_frame)

        # Кнопки управления настройками
        buttons_frame = QFrame()
        buttons_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 8px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        buttons_layout = QHBoxLayout(buttons_frame)

        self.save_btn = QPushButton("💾 Сохранить все")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: 1px solid #2ecc71;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        buttons_layout.addWidget(self.save_btn)

        self.reset_btn = QPushButton("↩️ Сбросить")
        self.reset_btn.clicked.connect(self.reset_settings)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: 1px solid #f1c40f;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #f1c40f;
            }
            QPushButton:pressed {
                background-color: #d68910;
            }
        """)
        buttons_layout.addWidget(self.reset_btn)

        self.default_btn = QPushButton("🔄 По умолчанию")
        self.default_btn.clicked.connect(self.load_default_settings)
        self.default_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        buttons_layout.addWidget(self.default_btn)

        buttons_layout.addStretch()
        scroll_layout.addWidget(buttons_frame)

        # Информация о текущих настройках
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 8px;
                padding: 8px;
                margin-top: 5px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)

        info_label = QLabel("ℹ️ Настройки сохраняются автоматически при закрытии приложения")
        info_label.setFont(QFont("Arial", 9))
        info_label.setStyleSheet("color: #bdc3c7;")
        info_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(info_label)

        scroll_layout.addWidget(info_frame)

        scroll_layout.addStretch()

        # Устанавливаем scroll area
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

    def setup_interface_settings(self):
        """Настройки интерфейса"""
        interface_group = QGroupBox("🎨 Настройки интерфейса")
        interface_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #ffffff;
                border: 2px solid #34495e;
                border-radius: 8px;
                margin-top: 5px;
                padding-top: 12px;
                background-color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #9b59b6;
            }
        """)

        interface_layout = QVBoxLayout(interface_group)
        interface_layout.setSpacing(12)
        interface_layout.setContentsMargins(12, 15, 12, 12)

        # Сетка для настроек
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setColumnStretch(1, 1)

        # Тема интерфейса
        theme_label = QLabel("Цветовая тема:")
        theme_label.setFont(QFont("Arial", 10))
        theme_label.setStyleSheet("color: #ecf0f1;")

        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "Темная (по умолчанию)",
            "Светлая",
            "Синяя",
            "Зеленая",
            "Фиолетовая",
            "Оранжевая"
        ])
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 6px;
                font-size: 11px;
                min-height: 30px;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #2c3e50;
                color: #ffffff;
                border: 1px solid #34495e;
                selection-background-color: #3498db;
                selection-color: white;
                font-size: 11px;
            }
        """)
        grid_layout.addWidget(theme_label, 0, 0)
        grid_layout.addWidget(self.theme_combo, 0, 1)

        # Прозрачность окон
        opacity_label = QLabel("Прозрачность окон:")
        opacity_label.setFont(QFont("Arial", 10))
        opacity_label.setStyleSheet("color: #ecf0f1;")

        opacity_slider_layout = QHBoxLayout()

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #34495e;
                height: 8px;
                background: #1e1e1e;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #2980b9;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #2980b9;
                border: 1px solid #21618c;
            }
        """)

        self.opacity_label = QLabel("100%")
        self.opacity_label.setFont(QFont("Arial", 10))
        self.opacity_label.setStyleSheet("color: #3498db; min-width: 40px;")
        self.opacity_label.setAlignment(Qt.AlignRight)

        self.opacity_slider.valueChanged.connect(
            lambda value: self.opacity_label.setText(f"{value}%")
        )

        opacity_slider_layout.addWidget(self.opacity_slider)
        opacity_slider_layout.addWidget(self.opacity_label)

        grid_layout.addWidget(opacity_label, 1, 0)
        grid_layout.addLayout(opacity_slider_layout, 1, 1)

        # Анимации
        self.animations_check = QCheckBox("Включить анимации")
        self.animations_check.setFont(QFont("Arial", 10))
        self.animations_check.setStyleSheet("""
            QCheckBox {
                color: #ecf0f1;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #34495e;
                border-radius: 3px;
                background-color: #1e1e1e;
            }
            QCheckBox::indicator:checked {
                background-color: #9b59b6;
                border: 1px solid #8e44ad;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #5d7b8a;
            }
        """)
        grid_layout.addWidget(self.animations_check, 2, 0, 1, 2)

        # Эффекты тени
        self.shadows_check = QCheckBox("Включить тени окон")
        self.shadows_check.setFont(QFont("Arial", 10))
        self.shadows_check.setStyleSheet(self.animations_check.styleSheet())
        grid_layout.addWidget(self.shadows_check, 3, 0, 1, 2)

        # Стиль кнопок
        button_style_label = QLabel("Стиль кнопок:")
        button_style_label.setFont(QFont("Arial", 10))
        button_style_label.setStyleSheet("color: #ecf0f1;")

        self.button_style_combo = QComboBox()
        self.button_style_combo.addItems([
            "Стандартный",
            "Закругленный",
            "Плоский",
            "С градиентом"
        ])
        self.button_style_combo.setStyleSheet(self.theme_combo.styleSheet())
        grid_layout.addWidget(button_style_label, 4, 0)
        grid_layout.addWidget(self.button_style_combo, 4, 1)

        interface_layout.addLayout(grid_layout)
        return interface_group

    def setup_model_settings(self):
        """Настройки модели"""
        model_group = QGroupBox("🧠 Настройки модели")
        model_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #ffffff;
                border: 1px solid #34495e;
                border-radius: 8px;
                margin-top: 5px;
                padding-top: 12px;
                background-color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #3498db;
            }
        """)

        model_layout = QVBoxLayout(model_group)
        model_layout.setSpacing(10)
        model_layout.setContentsMargins(12, 15, 12, 12)

        # Выбор модели из списка
        model_form = QFormLayout()
        model_form.setSpacing(8)
        model_form.setLabelAlignment(Qt.AlignLeft)

        model_label = QLabel("Выбор модели:")
        model_label.setFont(QFont("Arial", 10))
        model_label.setStyleSheet("color: #ecf0f1;")

        self.model_combo = QComboBox()
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 6px;
                font-size: 11px;
                min-height: 30px;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #2c3e50;
                color: #ffffff;
                border: 1px solid #34495e;
                selection-background-color: #3498db;
                selection-color: white;
                font-size: 11px;
            }
        """)

        # Поиск доступных моделей
        self.find_available_models()
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)

        model_form.addRow(model_label, self.model_combo)
        model_layout.addLayout(model_form)

        # Параметры модели
        params_layout = QHBoxLayout()
        params_layout.setSpacing(15)

        threshold_label = QLabel("Порог уверенности:")
        threshold_label.setFont(QFont("Arial", 10))
        threshold_label.setStyleSheet("color: #ecf0f1;")
        params_layout.addWidget(threshold_label)

        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.1, 1.0)
        self.threshold_spin.setSingleStep(0.05)
        self.threshold_spin.setValue(0.7)
        self.threshold_spin.setSuffix(" %")
        self.threshold_spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 6px;
                font-size: 11px;
                min-height: 30px;
                min-width: 100px;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                background-color: #34495e;
                border: 1px solid #4a6572;
                border-radius: 3px;
                width: 20px;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #4a6572;
            }
        """)
        params_layout.addWidget(self.threshold_spin)

        params_layout.addStretch()
        model_layout.addLayout(params_layout)

        # Информация о модели
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border: 1px solid #4a6572;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)

        self.model_info_label = QLabel("Модель: не выбрана")
        self.model_info_label.setFont(QFont("Arial", 10))
        self.model_info_label.setStyleSheet("color: #bdc3c7;")
        info_layout.addWidget(self.model_info_label)

        model_layout.addWidget(info_frame)

        return model_group

    def setup_ui_settings(self):
        """Настройки UI"""
        ui_group = QGroupBox("⚙ Дополнительные настройки")
        ui_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #ffffff;
                border: 1px solid #34495e;
                border-radius: 8px;
                margin-top: 5px;
                padding-top: 12px;
                background-color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #e74c3c;
            }
        """)

        ui_layout = QVBoxLayout(ui_group)
        ui_layout.setSpacing(12)
        ui_layout.setContentsMargins(12, 15, 12, 12)

        # Размер шрифта
        font_form = QFormLayout()
        font_form.setSpacing(8)

        font_label = QLabel("Размер шрифта:")
        font_label.setFont(QFont("Arial", 10))
        font_label.setStyleSheet("color: #ecf0f1;")

        self.font_spin = QSpinBox()
        self.font_spin.setRange(8, 16)
        self.font_spin.setValue(10)
        self.font_spin.setSuffix(" pt")
        self.font_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 6px;
                font-size: 11px;
                min-height: 30px;
                min-width: 100px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #34495e;
                border: 1px solid #4a6572;
                border-radius: 3px;
                width: 20px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #4a6572;
            }
        """)
        self.font_spin.valueChanged.connect(self.on_font_size_changed)

        font_form.addRow(font_label, self.font_spin)
        ui_layout.addLayout(font_form)

        # Стиль шрифта
        font_style_form = QFormLayout()
        font_style_form.setSpacing(8)

        font_style_label = QLabel("Стиль шрифта:")
        font_style_label.setFont(QFont("Arial", 10))
        font_style_label.setStyleSheet("color: #ecf0f1;")

        self.font_style_combo = QComboBox()
        self.font_style_combo.addItems(["Arial", "Segoe UI", "Verdana", "Tahoma", "Calibri"])
        self.font_style_combo.setStyleSheet(self.model_combo.styleSheet())
        font_style_form.addRow(font_style_label, self.font_style_combo)
        ui_layout.addLayout(font_style_form)

        # Дополнительные настройки
        options_frame = QFrame()
        options_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border: 1px solid #4a6572;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        options_layout = QVBoxLayout(options_frame)
        options_layout.setSpacing(8)

        self.autosave_check = QCheckBox("Автосохранение результатов")
        self.autosave_check.setFont(QFont("Arial", 10))
        self.autosave_check.setStyleSheet("""
            QCheckBox {
                color: #ecf0f1;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #34495e;
                border-radius: 3px;
                background-color: #1e1e1e;
            }
            QCheckBox::indicator:checked {
                background-color: #27ae60;
                border: 1px solid #2ecc71;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #5d7b8a;
            }
        """)
        options_layout.addWidget(self.autosave_check)

        self.show_preview_check = QCheckBox("Показывать превью изображений")
        self.show_preview_check.setFont(QFont("Arial", 10))
        self.show_preview_check.setStyleSheet("""
            QCheckBox {
                color: #ecf0f1;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #34495e;
                border-radius: 3px;
                background-color: #1e1e1e;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border: 1px solid #2980b9;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #5d7b8a;
            }
        """)
        options_layout.addWidget(self.show_preview_check)

        self.show_tooltips_check = QCheckBox("Показывать подсказки")
        self.show_tooltips_check.setFont(QFont("Arial", 10))
        self.show_tooltips_check.setStyleSheet(self.autosave_check.styleSheet())
        options_layout.addWidget(self.show_tooltips_check)

        ui_layout.addWidget(options_frame)

        return ui_group

    def find_available_models(self):
        """Поиск доступных моделей в папках"""
        self.model_combo.clear()

        # Добавляем стандартные пути поиска
        search_paths = [
            'models',
            '../models',
            '../../models',
            os.path.join(os.path.dirname(__file__), '..', 'models'),
            os.path.join(os.path.dirname(__file__), 'models'),
        ]

        found_models = []

        # Поиск файлов моделей
        for path in search_paths:
            if os.path.exists(path) and os.path.isdir(path):
                for file in os.listdir(path):
                    if file.lower().endswith(('.pth', '.pt', '.onnx')):
                        full_path = os.path.join(path, file)
                        found_models.append((file, full_path))

        # Добавляем в комбобокс
        self.model_combo.addItem("-- Выберите модель --", "")

        if found_models:
            for file_name, full_path in found_models:
                display_text = f"{file_name} ({os.path.dirname(full_path)})"
                self.model_combo.addItem(display_text, full_path)
        else:
            self.model_combo.addItem("❌ Модели не найдены", "")

        # Добавляем опцию выбора файла
        self.model_combo.addItem("📁 Выбрать файл модели...", "browse")

    def on_model_changed(self, index):
        """Обработка выбора модели"""
        if index > 0:  # Не первый элемент (пустой)
            data = self.model_combo.itemData(index)

            if data == "browse":
                # Открываем диалог выбора файла
                path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Выберите файл модели",
                    "",
                    "Model Files (*.pth *.pt *.onnx);;All Files (*)"
                )
                if path:
                    # Добавляем выбранный файл в список
                    file_name = os.path.basename(path)
                    display_text = f"{file_name} (выбранный файл)"
                    self.model_combo.insertItem(1, display_text, path)
                    self.model_combo.setCurrentIndex(1)
                    self.update_model_info(path)
                else:
                    # Если файл не выбран, возвращаемся к предыдущему
                    self.model_combo.setCurrentIndex(0)
            else:
                self.update_model_info(data)

    def update_model_info(self, model_path):
        """Обновление информации о модели"""
        if model_path and os.path.exists(model_path):
            file_name = os.path.basename(model_path)
            file_size = os.path.getsize(model_path) / (1024 * 1024)  # в MB

            self.model_info_label.setText(
                f"✅ Модель: {file_name}\n"
                f"📁 Путь: {os.path.dirname(model_path)}\n"
                f"📊 Размер: {file_size:.2f} MB"
            )
            self.model_info_label.setStyleSheet("color: #27ae60; font-size: 10px;")
        else:
            self.model_info_label.setText("⚠ Модель не выбрана или не найдена")
            self.model_info_label.setStyleSheet("color: #e74c3c; font-size: 10px;")

    def on_font_size_changed(self, value):
        """Предпросмотр размера шрифта"""
        self.main_window.update_status(f"Размер шрифта: {value} pt")

    def load_settings(self):
        """Загрузка настроек из реестра"""
        # Настройки модели
        saved_model_path = self.settings.value("model/path", "")
        if saved_model_path and os.path.exists(saved_model_path):
            # Ищем путь в комбобоксе
            for i in range(self.model_combo.count()):
                if self.model_combo.itemData(i) == saved_model_path:
                    self.model_combo.setCurrentIndex(i)
                    self.update_model_info(saved_model_path)
                    break

        self.threshold_spin.setValue(self.settings.value("model/threshold", 0.7, type=float))

        # НАСТРОЙКИ ИНТЕРФЕЙСА
        self.theme_combo.setCurrentText(self.settings.value("interface/theme", "Темная (по умолчанию)"))
        self.opacity_slider.setValue(self.settings.value("interface/opacity", 100, type=int))
        self.animations_check.setChecked(self.settings.value("interface/animations", True, type=bool))
        self.shadows_check.setChecked(self.settings.value("interface/shadows", True, type=bool))
        self.button_style_combo.setCurrentText(self.settings.value("interface/button_style", "Стандартный"))

        # Настройки UI
        self.font_spin.setValue(self.settings.value("ui/font_size", 10, type=int))
        self.font_style_combo.setCurrentText(self.settings.value("ui/font_style", "Arial"))
        self.autosave_check.setChecked(self.settings.value("ui/autosave", True, type=bool))
        self.show_preview_check.setChecked(self.settings.value("ui/show_preview", True, type=bool))
        self.show_tooltips_check.setChecked(self.settings.value("ui/show_tooltips", True, type=bool))

    def save_settings(self):
        """Сохранение настроек в реестр"""
        try:
            # Настройки модели
            model_path = self.model_combo.currentData()
            if model_path and model_path != "browse":
                self.settings.setValue("model/path", model_path)
            self.settings.setValue("model/threshold", self.threshold_spin.value())

            # НАСТРОЙКИ ИНТЕРФЕЙСА
            self.settings.setValue("interface/theme", self.theme_combo.currentText())
            self.settings.setValue("interface/opacity", self.opacity_slider.value())
            self.settings.setValue("interface/animations", self.animations_check.isChecked())
            self.settings.setValue("interface/shadows", self.shadows_check.isChecked())
            self.settings.setValue("interface/button_style", self.button_style_combo.currentText())

            # Настройки UI
            self.settings.setValue("ui/font_size", self.font_spin.value())
            self.settings.setValue("ui/font_style", self.font_style_combo.currentText())
            self.settings.setValue("ui/autosave", self.autosave_check.isChecked())
            self.settings.setValue("ui/show_preview", self.show_preview_check.isChecked())
            self.settings.setValue("ui/show_tooltips", self.show_tooltips_check.isChecked())

            self.settings.sync()

            # Применяем настройки к модели
            self.apply_model_settings()

            # Применяем настройки интерфейса
            interface_settings = {
                'theme': self.theme_combo.currentText(),
                'opacity': self.opacity_slider.value(),
                'animations': self.animations_check.isChecked(),
                'shadows': self.shadows_check.isChecked(),
                'button_style': self.button_style_combo.currentText()
            }
            self.apply_interface_changes(interface_settings)

            QMessageBox.information(self, "Успех", "Все настройки успешно сохранены и применены")
            self.main_window.update_status("Настройки сохранены")

        except Exception as e:
            self.show_error(f"Ошибка сохранения настроек: {e}")

    def apply_interface_settings(self):
        """Применение настроек интерфейса"""
        try:
            # Получаем настройки интерфейса
            interface_settings = {
                'theme': self.theme_combo.currentText(),
                'opacity': self.opacity_slider.value(),
                'animations': self.animations_check.isChecked(),
                'shadows': self.shadows_check.isChecked(),
                'button_style': self.button_style_combo.currentText(),
                'font_size': self.font_spin.value(),
                'font_style': self.font_style_combo.currentText(),
                'show_tooltips': self.show_tooltips_check.isChecked()
            }

            # Применяем настройки интерфейса
            self.apply_interface_changes(interface_settings)

            # Сохраняем настройки интерфейса
            self.settings.setValue("interface/theme", interface_settings['theme'])
            self.settings.setValue("interface/opacity", interface_settings['opacity'])
            self.settings.setValue("interface/animations", interface_settings['animations'])
            self.settings.setValue("interface/shadows", interface_settings['shadows'])
            self.settings.setValue("interface/button_style", interface_settings['button_style'])
            self.settings.sync()

            # Обновляем статус
            self.main_window.update_status("Настройки интерфейса применены")

        except Exception as e:
            self.show_error(f"Ошибка применения настроек интерфейса: {e}")

    def apply_interface_changes(self, settings):
        """Применение изменений интерфейса"""
        try:
            # Применение темы - ко всему приложению
            theme_style = self.get_theme_style(settings['theme'])

            # Применяем стиль к главному окну
            if hasattr(self.main_window, 'setStyleSheet'):
                self.main_window.setStyleSheet(theme_style)

            # Применяем стиль к текущему виджету
            self.setStyleSheet(theme_style)

            # Применение прозрачности
            if hasattr(self.main_window, 'setWindowOpacity'):
                opacity = settings['opacity'] / 100.0
                self.main_window.setWindowOpacity(opacity)

            # Применение стиля кнопок
            self.apply_button_style(settings['button_style'])

            # Применение настроек шрифта
            self.apply_font_settings(settings['font_size'], settings['font_style'])

            # Обновляем статус
            status_messages = []
            if settings['animations']:
                status_messages.append("анимации включены")
            else:
                status_messages.append("анимации выключены")

            if settings['show_tooltips']:
                status_messages.append("подсказки включены")
            else:
                status_messages.append("подсказки выключены")

            self.main_window.update_status(f"Применена тема: {settings['theme']} ({', '.join(status_messages)})")

            return True

        except Exception as e:
            print(f"Ошибка применения интерфейса: {e}")
            return False

    def get_theme_style(self, theme_name):
        """Получение стиля для выбранной темы"""
        if theme_name == "Темная (по умолчанию)":
            return """
                QMainWindow, QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QGroupBox {
                    border: 2px solid #555555;
                    border-radius: 10px;
                    margin-top: 10px;
                    background-color: #2c3e50;
                }
                QGroupBox::title {
                    color: #3498db;
                }
                QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #34495e;
                }
            """
        elif theme_name == "Светлая":
            return """
                QMainWindow, QWidget {
                    background-color: #f5f5f5;
                    color: #333333;
                }
                QLabel {
                    color: #333333;
                }
                QGroupBox {
                    border: 2px solid #cccccc;
                    border-radius: 10px;
                    margin-top: 10px;
                    background-color: #ffffff;
                }
                QGroupBox::title {
                    color: #2980b9;
                }
                QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #cccccc;
                }
            """
        elif theme_name == "Синяя":
            return """
                QMainWindow, QWidget {
                    background-color: #1c2833;
                    color: #ecf0f1;
                }
                QLabel {
                    color: #ecf0f1;
                }
                QGroupBox {
                    border: 2px solid #3498db;
                    border-radius: 10px;
                    margin-top: 10px;
                    background-color: #2c3e50;
                }
                QGroupBox::title {
                    color: #3498db;
                }
                QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #3498db;
                }
            """
        elif theme_name == "Зеленая":
            return """
                QMainWindow, QWidget {
                    background-color: #1a252f;
                    color: #ecf0f1;
                }
                QLabel {
                    color: #ecf0f1;
                }
                QGroupBox {
                    border: 2px solid #27ae60;
                    border-radius: 10px;
                    margin-top: 10px;
                    background-color: #2c3e50;
                }
                QGroupBox::title {
                    color: #27ae60;
                }
                QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #27ae60;
                }
            """
        elif theme_name == "Фиолетовая":
            return """
                QMainWindow, QWidget {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
                QLabel {
                    color: #ecf0f1;
                }
                QGroupBox {
                    border: 2px solid #9b59b6;
                    border-radius: 10px;
                    margin-top: 10px;
                    background-color: #34495e;
                }
                QGroupBox::title {
                    color: #9b59b6;
                }
                QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #9b59b6;
                }
            """
        elif theme_name == "Оранжевая":
            return """
                QMainWindow, QWidget {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
                QLabel {
                    color: #ecf0f1;
                }
                QGroupBox {
                    border: 2px solid #e67e22;
                    border-radius: 10px;
                    margin-top: 10px;
                    background-color: #34495e;
                }
                QGroupBox::title {
                    color: #e67e22;
                }
                QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #e67e22;
                }
            """
        return ""

    def apply_button_style(self, style_name):
        """Применение стиля кнопок"""
        # Базовые стили для кнопок
        apply_base_style = """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
                border-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #229954;
                border-color: #1e8449;
            }
        """

        save_base_style = """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: 1px solid #2ecc71;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """

        reset_base_style = """
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: 1px solid #f1c40f;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #f1c40f;
            }
            QPushButton:pressed {
                background-color: #d68910;
            }
        """

        default_base_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """

        if style_name == "Закругленный":
            rounded_style = "border-radius: 15px;"
            self.apply_btn.setStyleSheet(apply_base_style + rounded_style)
            self.save_btn.setStyleSheet(save_base_style + rounded_style)
            self.reset_btn.setStyleSheet(reset_base_style + rounded_style)
            self.default_btn.setStyleSheet(default_base_style + rounded_style)

        elif style_name == "Плоский":
            flat_style = "border: none; border-radius: 3px;"
            self.apply_btn.setStyleSheet(apply_base_style + flat_style)
            self.save_btn.setStyleSheet(save_base_style + flat_style)
            self.reset_btn.setStyleSheet(reset_base_style + flat_style)
            self.default_btn.setStyleSheet(default_base_style + flat_style)

        elif style_name == "С градиентом":
            gradient_apply = """
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #229954);
            """
            gradient_save = """
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #229954);
            """
            gradient_reset = """
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f39c12, stop:1 #d68910);
            """
            gradient_default = """
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
            """

            self.apply_btn.setStyleSheet(apply_base_style + gradient_apply)
            self.save_btn.setStyleSheet(save_base_style + gradient_save)
            self.reset_btn.setStyleSheet(reset_base_style + gradient_reset)
            self.default_btn.setStyleSheet(default_base_style + gradient_default)

        else:  # Стандартный
            self.apply_btn.setStyleSheet(apply_base_style)
            self.save_btn.setStyleSheet(save_base_style)
            self.reset_btn.setStyleSheet(reset_base_style)
            self.default_btn.setStyleSheet(default_base_style)

    def apply_font_settings(self, size, style):
        """Применение настроек шрифта"""
        try:
            font = QFont(style, size)

            # Применяем шрифт к главному окну
            if hasattr(self.main_window, 'setFont'):
                self.main_window.setFont(font)

            # Применяем шрифт к текущему виджету
            self.setFont(font)

            # Обновляем шрифт для всех виджетов
            self.update_font_recursive(self, font)

        except Exception as e:
            print(f"Ошибка применения шрифта: {e}")

    def update_font_recursive(self, widget, font):
        """Рекурсивное обновление шрифта для всех дочерних виджетов"""
        try:
            widget.setFont(font)

            # Рекурсивно обновляем дочерние виджеты
            for child in widget.children():
                if isinstance(child, QWidget):
                    self.update_font_recursive(child, font)

        except Exception as e:
            print(f"Ошибка обновления шрифта: {e}")

    def reset_settings(self):
        """Сброс настроек к текущим сохраненным"""
        reply = QMessageBox.question(self, "Подтверждение",
                                     "Сбросить настройки к последним сохраненным?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.load_settings()
            self.main_window.update_status("Настройки сброшены")

    def load_default_settings(self):
        """Загрузка默认ных настроек"""
        reply = QMessageBox.question(self, "Подтверждение",
                                     "Загрузить默认ные настройки? Текущие будут потеряны.",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Сбрасываем на默认ные значения
            self.model_combo.setCurrentIndex(0)
            self.threshold_spin.setValue(0.7)

            # Настройки интерфейса
            self.theme_combo.setCurrentText("Темная (по умолчанию)")
            self.opacity_slider.setValue(100)
            self.animations_check.setChecked(True)
            self.shadows_check.setChecked(True)
            self.button_style_combo.setCurrentText("Стандартный")

            # Настройки UI
            self.font_spin.setValue(10)
            self.font_style_combo.setCurrentText("Arial")
            self.autosave_check.setChecked(True)
            self.show_preview_check.setChecked(True)
            self.show_tooltips_check.setChecked(True)

            self.update_model_info("")
            self.main_window.update_status("Загружены默认ные настройки")

    def apply_model_settings(self):
        """Применение настроек модели"""
        try:
            model_path = self.model_combo.currentData()
            if model_path and model_path != "browse" and os.path.exists(model_path):
                # Обновляем модель в обработчике
                from .model_handler import model_handler
                model_handler.model_path = model_path
                if model_handler.load_model():
                    self.main_window.update_status(f"Модель загружена: {os.path.basename(model_path)}")
                    print("Настройки модели применены")
                else:
                    self.show_error("Не удалось загрузить модель")
        except Exception as e:
            print(f"Ошибка применения настроек модели: {e}")

    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)
        self.main_window.update_status(f"Ошибка: {message}")