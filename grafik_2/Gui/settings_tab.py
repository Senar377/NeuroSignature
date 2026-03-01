# Gui/settings_tab.py
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QGroupBox, QComboBox,
    QCheckBox, QSpinBox, QSlider,
    QScrollArea, QFrame, QFormLayout, QGridLayout,
    QSizePolicy
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QFont


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
        layout.addWidget(title_label)

        # Scroll area для настроек
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(15, 15, 15, 15)

        # НАСТРОЙКИ ИНТЕРФЕЙСА
        interface_group = self.setup_interface_settings()
        scroll_layout.addWidget(interface_group)

        # Настройки UI
        ui_group = self.setup_ui_settings()
        scroll_layout.addWidget(ui_group)

        # Кнопка "Применить"
        apply_frame = QFrame()
        apply_frame.setFrameStyle(QFrame.Box)
        apply_layout = QVBoxLayout(apply_frame)

        self.apply_btn = QPushButton("✅ Применить настройки интерфейса")
        self.apply_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.apply_btn.setFixedHeight(45)
        self.apply_btn.clicked.connect(self.apply_interface_settings)
        apply_layout.addWidget(self.apply_btn)

        apply_desc = QLabel(
            "Настройки интерфейса применяются немедленно.\n"
            "Все изменения автоматически сохраняются."
        )
        apply_desc.setFont(QFont("Arial", 9))
        apply_desc.setAlignment(Qt.AlignCenter)
        apply_desc.setWordWrap(True)
        apply_layout.addWidget(apply_desc)

        scroll_layout.addWidget(apply_frame)

        # Кнопки управления
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)

        self.reset_btn = QPushButton("↩️ Сбросить")
        self.reset_btn.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(self.reset_btn)

        self.default_btn = QPushButton("🔄 По умолчанию")
        self.default_btn.clicked.connect(self.load_default_settings)
        buttons_layout.addWidget(self.default_btn)

        buttons_layout.addStretch()
        scroll_layout.addWidget(buttons_frame)

        # Информация о настройках
        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)

        info_label = QLabel("ℹ️ Настройки сохраняются автоматически")
        info_label.setFont(QFont("Arial", 9))
        info_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(info_label)

        scroll_layout.addWidget(info_frame)
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

    def setup_interface_settings(self):
        """Настройки интерфейса"""
        interface_group = QGroupBox("🎨 Настройки интерфейса")

        grid_layout = QGridLayout(interface_group)
        grid_layout.setSpacing(15)

        # Тема интерфейса
        theme_label = QLabel("Цветовая тема:")
        theme_label.setFont(QFont("Arial", 10))

        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "Светлая",
            "Темная"
        ])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        grid_layout.addWidget(theme_label, 0, 0)
        grid_layout.addWidget(self.theme_combo, 0, 1)

        # Прозрачность окон
        opacity_label = QLabel("Прозрачность окон:")
        opacity_label.setFont(QFont("Arial", 10))

        opacity_slider_layout = QHBoxLayout()

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setTickPosition(QSlider.TicksBelow)
        self.opacity_slider.setTickInterval(10)

        self.opacity_label = QLabel("100%")
        self.opacity_label.setFont(QFont("Arial", 10))
        self.opacity_label.setMinimumWidth(40)
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
        grid_layout.addWidget(self.animations_check, 2, 0, 1, 2)

        # Эффекты тени
        self.shadows_check = QCheckBox("Включить тени окон")
        self.shadows_check.setFont(QFont("Arial", 10))
        grid_layout.addWidget(self.shadows_check, 3, 0, 1, 2)

        # Стиль кнопок
        button_style_label = QLabel("Стиль кнопок:")
        button_style_label.setFont(QFont("Arial", 10))

        self.button_style_combo = QComboBox()
        self.button_style_combo.addItems([
            "Стандартный",
            "Закругленный",
            "Плоский",
            "С градиентом"
        ])
        grid_layout.addWidget(button_style_label, 4, 0)
        grid_layout.addWidget(self.button_style_combo, 4, 1)

        return interface_group

    def setup_ui_settings(self):
        """Настройки UI"""
        ui_group = QGroupBox("⚙ Дополнительные настройки")

        form_layout = QFormLayout(ui_group)
        form_layout.setSpacing(10)

        # Размер шрифта
        self.font_spin = QSpinBox()
        self.font_spin.setRange(8, 16)
        self.font_spin.setValue(10)
        self.font_spin.setSuffix(" pt")
        form_layout.addRow("Размер шрифта:", self.font_spin)

        # Стиль шрифта
        self.font_style_combo = QComboBox()
        self.font_style_combo.addItems(["Arial", "Segoe UI", "Verdana", "Tahoma", "Calibri"])
        form_layout.addRow("Стиль шрифта:", self.font_style_combo)

        # Дополнительные настройки
        self.autosave_check = QCheckBox("Автосохранение результатов")
        form_layout.addRow("", self.autosave_check)

        self.show_preview_check = QCheckBox("Показывать превью изображений")
        form_layout.addRow("", self.show_preview_check)

        self.show_tooltips_check = QCheckBox("Показывать подсказки")
        form_layout.addRow("", self.show_tooltips_check)

        return ui_group

    def on_theme_changed(self, theme_name):
        """Обработка изменения темы"""
        if theme_name == "Темная (по умолчанию)":
            theme_id = "dark"
        else:
            theme_id = "light"

        self.main_window.change_theme(theme_id)

    def load_settings(self):
        """Загрузка настроек из реестра"""
        theme = self.settings.value("interface/theme", "Светлая")
        self.theme_combo.setCurrentText(theme)

        opacity = self.settings.value("interface/opacity", 100, type=int)
        self.opacity_slider.setValue(opacity)

        animations = self.settings.value("interface/animations", True, type=bool)
        self.animations_check.setChecked(animations)

        shadows = self.settings.value("interface/shadows", True, type=bool)
        self.shadows_check.setChecked(shadows)

        button_style = self.settings.value("interface/button_style", "Стандартный")
        self.button_style_combo.setCurrentText(button_style)

        font_size = self.settings.value("ui/font_size", 10, type=int)
        self.font_spin.setValue(font_size)

        font_style = self.settings.value("ui/font_style", "Arial")
        self.font_style_combo.setCurrentText(font_style)

        autosave = self.settings.value("ui/autosave", True, type=bool)
        self.autosave_check.setChecked(autosave)

        show_preview = self.settings.value("ui/show_preview", True, type=bool)
        self.show_preview_check.setChecked(show_preview)

        show_tooltips = self.settings.value("ui/show_tooltips", True, type=bool)
        self.show_tooltips_check.setChecked(show_tooltips)

    def save_settings(self):
        """Сохранение настроек"""
        try:
            self.settings.setValue("interface/theme", self.theme_combo.currentText())
            self.settings.setValue("interface/opacity", self.opacity_slider.value())
            self.settings.setValue("interface/animations", self.animations_check.isChecked())
            self.settings.setValue("interface/shadows", self.shadows_check.isChecked())
            self.settings.setValue("interface/button_style", self.button_style_combo.currentText())

            self.settings.setValue("ui/font_size", self.font_spin.value())
            self.settings.setValue("ui/font_style", self.font_style_combo.currentText())
            self.settings.setValue("ui/autosave", self.autosave_check.isChecked())
            self.settings.setValue("ui/show_preview", self.show_preview_check.isChecked())
            self.settings.setValue("ui/show_tooltips", self.show_tooltips_check.isChecked())

            self.settings.sync()
            return True

        except Exception as e:
            self.show_error(f"Ошибка сохранения настроек: {e}")
            return False

    def apply_interface_settings(self):
        """Применение настроек интерфейса"""
        if self.save_settings():
            opacity = self.opacity_slider.value() / 100.0
            self.main_window.setWindowOpacity(opacity)

            self.apply_font_settings()

            self.main_window.update_status("Настройки интерфейса применены")

            QMessageBox.information(self, "Успех", "Настройки успешно применены")

    def apply_font_settings(self):
        """Применение настроек шрифта"""
        font = QFont(
            self.font_style_combo.currentText(),
            self.font_spin.value()
        )
        self.main_window.setFont(font)

    def reset_settings(self):
        """Сброс настроек к последним сохраненным"""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Сбросить настройки к последним сохраненным?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.load_settings()
            self.main_window.update_status("Настройки сброшены")

    def load_default_settings(self):
        """Загрузка настроек по умолчанию"""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Загрузить настройки по умолчанию?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.theme_combo.setCurrentText("Светлая")
            self.opacity_slider.setValue(100)
            self.animations_check.setChecked(True)
            self.shadows_check.setChecked(True)
            self.button_style_combo.setCurrentText("Стандартный")
            self.font_spin.setValue(10)
            self.font_style_combo.setCurrentText("Arial")
            self.autosave_check.setChecked(True)
            self.show_preview_check.setChecked(True)
            self.show_tooltips_check.setChecked(True)

            self.apply_interface_settings()
            self.main_window.update_status("Загружены настройки по умолчанию")

    def show_error(self, message):
        """Отображение ошибки"""
        QMessageBox.critical(self, "Ошибка", message)
        self.main_window.update_status(f"Ошибка: {message}")