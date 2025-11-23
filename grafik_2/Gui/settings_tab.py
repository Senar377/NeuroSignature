import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QMessageBox, QGroupBox, QComboBox,
                               QCheckBox, QSpinBox, QDoubleSpinBox, QLineEdit,
                               QFileDialog, QScrollArea, QFrame, QSlider)
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
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок
        title_label = QLabel("Настройки приложения")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Scroll area для настроек
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Настройки модели
        model_group = self.setup_model_settings()
        scroll_layout.addWidget(model_group)

        # Настройки обработки
        processing_group = self.setup_processing_settings()
        scroll_layout.addWidget(processing_group)

        # Настройки интерфейса
        ui_group = self.setup_ui_settings()
        scroll_layout.addWidget(ui_group)

        # Настройки путей
        paths_group = self.setup_paths_settings()
        scroll_layout.addWidget(paths_group)

        # Кнопки управления настройками
        buttons_layout = QHBoxLayout()

        self.save_btn = QPushButton("Сохранить настройки")
        self.save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_btn)

        self.reset_btn = QPushButton("Сбросить к默认ным")
        self.reset_btn.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(self.reset_btn)

        self.default_btn = QPushButton("Загрузить默认ные")
        self.default_btn.clicked.connect(self.load_default_settings)
        buttons_layout.addWidget(self.default_btn)

        buttons_layout.addStretch()
        scroll_layout.addLayout(buttons_layout)

        scroll_layout.addStretch()

        # Устанавливаем scroll area
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

    def setup_model_settings(self):
        """Настройки модели"""
        model_group = QGroupBox("Настройки модели")
        model_layout = QVBoxLayout(model_group)

        # Выбор модели
        model_path_layout = QHBoxLayout()
        model_label = QLabel("Путь к модели:")
        self.model_path_edit = QLineEdit()
        self.model_path_edit.setPlaceholderText("Выберите файл модели .pth...")
        model_browse_btn = QPushButton("Обзор")
        model_browse_btn.clicked.connect(self.browse_model_path)
        model_path_layout.addWidget(model_label)
        model_path_layout.addWidget(self.model_path_edit)
        model_path_layout.addWidget(model_browse_btn)
        model_layout.addLayout(model_path_layout)

        # Параметры модели
        params_layout = QHBoxLayout()
        threshold_label = QLabel("Порог уверенности:")
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.1, 1.0)
        self.threshold_spin.setSingleStep(0.05)
        self.threshold_spin.setValue(0.7)
        self.threshold_spin.setSuffix(" %")
        params_layout.addWidget(threshold_label)
        params_layout.addWidget(self.threshold_spin)
        params_layout.addStretch()
        model_layout.addLayout(params_layout)

        # Информация о модели
        model_info_layout = QHBoxLayout()
        self.model_info_label = QLabel("Модель: не загружена")
        self.model_info_label.setStyleSheet("color: #888888; font-size: 11px;")
        model_info_layout.addWidget(self.model_info_label)
        model_info_layout.addStretch()

        self.reload_model_btn = QPushButton("Перезагрузить модель")
        self.reload_model_btn.clicked.connect(self.reload_model)
        model_info_layout.addWidget(self.reload_model_btn)
        model_layout.addLayout(model_info_layout)

        return model_group

    def setup_processing_settings(self):
        """Настройки обработки"""
        processing_group = QGroupBox("Настройки обработки изображений")
        processing_layout = QVBoxLayout(processing_group)

        # Качество обработки
        quality_layout = QHBoxLayout()
        quality_label = QLabel("Качество обработки:")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Высокое", "Среднее", "Быстрое"])
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        processing_layout.addLayout(quality_layout)

        # Предобработка
        self.auto_preprocess_check = QCheckBox("Автоматическая предобработка изображений")
        processing_layout.addWidget(self.auto_preprocess_check)

        self.enhance_contrast_check = QCheckBox("Улучшение контраста")
        processing_layout.addWidget(self.enhance_contrast_check)

        self.remove_noise_check = QCheckBox("Удаление шума")
        processing_layout.addWidget(self.remove_noise_check)

        # Размер изображения
        size_layout = QHBoxLayout()
        size_label = QLabel("Размер изображения:")
        self.size_combo = QComboBox()
        self.size_combo.addItems(["128x256", "256x512", "Исходный размер"])
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_combo)
        size_layout.addStretch()
        processing_layout.addLayout(size_layout)

        return processing_group

    def setup_ui_settings(self):
        """Настройки интерфейса"""
        ui_group = QGroupBox("Настройки интерфейса")
        ui_layout = QVBoxLayout(ui_group)

        # Тема
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Тема интерфейса:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Темная", "Светлая", "Системная"])
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        ui_layout.addLayout(theme_layout)

        # Размер шрифта
        font_layout = QHBoxLayout()
        font_label = QLabel("Размер шрифта:")
        self.font_spin = QSpinBox()
        self.font_spin.setRange(8, 16)
        self.font_spin.setSuffix(" pt")
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_spin)
        font_layout.addStretch()
        ui_layout.addLayout(font_layout)

        # Автосохранение
        self.autosave_check = QCheckBox("Автосохранение результатов")
        ui_layout.addWidget(self.autosave_check)

        self.show_preview_check = QCheckBox("Показывать превью изображений")
        ui_layout.addWidget(self.show_preview_check)

        return ui_group

    def setup_paths_settings(self):
        """Настройки путей"""
        paths_group = QGroupBox("Пути сохранения")
        paths_layout = QVBoxLayout(paths_group)

        # Папка результатов
        results_layout = QHBoxLayout()
        results_label = QLabel("Папка результатов:")
        self.results_path_edit = QLineEdit()
        self.results_path_edit.setPlaceholderText("Путь для сохранения результатов...")
        results_browse_btn = QPushButton("Обзор")
        results_browse_btn.clicked.connect(self.browse_results_path)
        results_layout.addWidget(results_label)
        results_layout.addWidget(self.results_path_edit)
        results_layout.addWidget(results_browse_btn)
        paths_layout.addLayout(results_layout)

        # Папка логов
        logs_layout = QHBoxLayout()
        logs_label = QLabel("Папка логов:")
        self.logs_path_edit = QLineEdit()
        self.logs_path_edit.setPlaceholderText("Путь для сохранения логов...")
        logs_browse_btn = QPushButton("Обзор")
        logs_browse_btn.clicked.connect(self.browse_logs_path)
        logs_layout.addWidget(logs_label)
        logs_layout.addWidget(self.logs_path_edit)
        logs_layout.addWidget(logs_browse_btn)
        paths_layout.addLayout(logs_layout)

        # Папка моделей
        models_layout = QHBoxLayout()
        models_label = QLabel("Папка моделей:")
        self.models_path_edit = QLineEdit()
        self.models_path_edit.setPlaceholderText("Путь к папке с моделями...")
        models_browse_btn = QPushButton("Обзор")
        models_browse_btn.clicked.connect(self.browse_models_path)
        models_layout.addWidget(models_label)
        models_layout.addWidget(self.models_path_edit)
        models_layout.addWidget(models_browse_btn)
        paths_layout.addLayout(models_layout)

        return paths_group

    def load_settings(self):
        """Загрузка настроек из реестра"""
        # Настройки модели
        self.model_path_edit.setText(self.settings.value("model/path", ""))
        self.threshold_spin.setValue(self.settings.value("model/threshold", 0.7, type=float))

        # Настройки обработки
        self.quality_combo.setCurrentText(self.settings.value("processing/quality", "Среднее"))
        self.auto_preprocess_check.setChecked(self.settings.value("processing/auto_preprocess", True, type=bool))
        self.enhance_contrast_check.setChecked(self.settings.value("processing/enhance_contrast", True, type=bool))
        self.remove_noise_check.setChecked(self.settings.value("processing/remove_noise", True, type=bool))
        self.size_combo.setCurrentText(self.settings.value("processing/size", "128x256"))

        # Настройки интерфейса
        self.theme_combo.setCurrentText(self.settings.value("ui/theme", "Темная"))
        self.font_spin.setValue(self.settings.value("ui/font_size", 10, type=int))
        self.autosave_check.setChecked(self.settings.value("ui/autosave", True, type=bool))
        self.show_preview_check.setChecked(self.settings.value("ui/show_preview", True, type=bool))

        # Настройки путей
        self.results_path_edit.setText(self.settings.value("paths/results", ""))
        self.logs_path_edit.setText(self.settings.value("paths/logs", ""))
        self.models_path_edit.setText(self.settings.value("paths/models", ""))

        # Обновляем информацию о модели
        self.update_model_info()

    def save_settings(self):
        """Сохранение настроек в реестр"""
        try:
            # Настройки модели
            self.settings.setValue("model/path", self.model_path_edit.text())
            self.settings.setValue("model/threshold", self.threshold_spin.value())

            # Настройки обработки
            self.settings.setValue("processing/quality", self.quality_combo.currentText())
            self.settings.setValue("processing/auto_preprocess", self.auto_preprocess_check.isChecked())
            self.settings.setValue("processing/enhance_contrast", self.enhance_contrast_check.isChecked())
            self.settings.setValue("processing/remove_noise", self.remove_noise_check.isChecked())
            self.settings.setValue("processing/size", self.size_combo.currentText())

            # Настройки интерфейса
            self.settings.setValue("ui/theme", self.theme_combo.currentText())
            self.settings.setValue("ui/font_size", self.font_spin.value())
            self.settings.setValue("ui/autosave", self.autosave_check.isChecked())
            self.settings.setValue("ui/show_preview", self.show_preview_check.isChecked())

            # Настройки путей
            self.settings.setValue("paths/results", self.results_path_edit.text())
            self.settings.setValue("paths/logs", self.logs_path_edit.text())
            self.settings.setValue("paths/models", self.models_path_edit.text())

            self.settings.sync()

            # Применяем настройки к модели
            self.apply_model_settings()

            QMessageBox.information(self, "Успех", "Настройки успешно сохранены и применены")
            self.main_window.update_status("Настройки сохранены")

        except Exception as e:
            self.show_error(f"Ошибка сохранения настроек: {e}")

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
            self.model_path_edit.clear()
            self.threshold_spin.setValue(0.7)

            self.quality_combo.setCurrentText("Среднее")
            self.auto_preprocess_check.setChecked(True)
            self.enhance_contrast_check.setChecked(True)
            self.remove_noise_check.setChecked(True)
            self.size_combo.setCurrentText("128x256")

            self.theme_combo.setCurrentText("Темная")
            self.font_spin.setValue(10)
            self.autosave_check.setChecked(True)
            self.show_preview_check.setChecked(True)

            self.results_path_edit.clear()
            self.logs_path_edit.clear()
            self.models_path_edit.clear()

            self.main_window.update_status("Загружены默认ные настройки")

    def apply_model_settings(self):
        """Применение настроек модели"""
        try:
            model_path = self.model_path_edit.text()
            if model_path and os.path.exists(model_path):
                # Обновляем модель в других вкладках
                if hasattr(self.main_window, 'processing_tab'):
                    self.main_window.processing_tab.model_handler.load_model()

                if hasattr(self.main_window, 'verification_tab'):
                    self.main_window.verification_tab.model_handler.load_model()

                self.update_model_info()
                print("Настройки модели применены")
        except Exception as e:
            print(f"Ошибка применения настроек модели: {e}")

    def update_model_info(self):
        """Обновление информации о модели"""
        model_path = self.model_path_edit.text()
        if model_path and os.path.exists(model_path):
            self.model_info_label.setText(f"Модель: {os.path.basename(model_path)}")
            self.model_info_label.setStyleSheet("color: #27ae60; font-size: 11px;")
        else:
            self.model_info_label.setText("Модель: не загружена (используется эмуляция)")
            self.model_info_label.setStyleSheet("color: #e74c3c; font-size: 11px;")

    def reload_model(self):
        """Перезагрузка модели"""
        self.apply_model_settings()
        QMessageBox.information(self, "Успех", "Модель перезагружена")

    def browse_model_path(self):
        """Выбор файла модели"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл модели",
            "",
            "Model Files (*.pth *.pt *.onnx);;All Files (*)"
        )
        if path:
            self.model_path_edit.setText(path)
            self.update_model_info()

    def browse_results_path(self):
        """Выбор папки для результатов"""
        path = QFileDialog.getExistingDirectory(self, "Выберите папку для результатов")
        if path:
            self.results_path_edit.setText(path)

    def browse_logs_path(self):
        """Выбор папки для логов"""
        path = QFileDialog.getExistingDirectory(self, "Выберите папку для логов")
        if path:
            self.logs_path_edit.setText(path)

    def browse_models_path(self):
        """Выбор папки для моделей"""
        path = QFileDialog.getExistingDirectory(self, "Выберите папку для моделей")
        if path:
            self.models_path_edit.setText(path)

    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)
        self.main_window.update_status(f"Ошибка: {message}")
