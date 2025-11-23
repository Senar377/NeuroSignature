import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QFrame, QComboBox,
                               QSlider, QFileDialog, QProgressBar, QTextEdit, QDialog,
                               QMessageBox, QCheckBox)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPixmap, QFont, QImage, QPainter, QColor, QLinearGradient
from PIL import Image, ImageOps
import torch
from neural_network import signature_recognition


class AnimatedButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._color = QColor("#4CAF50")
        self.animation = QPropertyAnimation(self, b"color")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def get_color(self):
        return self._color

    def set_color(self, color):
        self._color = color
        self.update()

    color = Property(QColor, get_color, set_color)

    def enterEvent(self, event):
        self.animation.setStartValue(self._color)
        self.animation.setEndValue(QColor("#45a049"))
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.setStartValue(self._color)
        self.animation.setEndValue(QColor("#4CAF50"))
        self.animation.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Градиентный фон
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, self._color.lighter(120))
        gradient.setColorAt(1, self._color.darker(120))

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

        # Текст
        painter.setPen(QColor("white"))
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())


class ImageDropLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                background-color: #fafafa;
                color: #666666;
                font-size: 14px;
            }
            QLabel:hover {
                border: 2px dashed #4CAF50;
                background-color: #f0f8f0;
            }
        """)
        self.setFixedSize(320, 220)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    border: 2px dashed #4CAF50;
                    border-radius: 10px;
                    background-color: #f0f8f0;
                    color: #4CAF50;
                    font-size: 14px;
                }
            """)

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                background-color: #fafafa;
                color: #666666;
                font-size: 14px;
            }
        """)

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                self.parent().load_image_from_path(file_path)

        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                background-color: #fafafa;
                color: #666666;
                font-size: 14px;
            }
        """)


class SignatureVerificationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.model_path = "models/best_model.pth"
        self.threshold = 70
        self.original_path = None
        self.test_path = None
        self.verification_history = []
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Signature Verification Scanner")
        self.setMinimumSize(1000, 700)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # Заголовок с иконкой
        header_layout = QHBoxLayout()

        title_label = QLabel("🔍 Сканер подписей")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Кнопка настроек
        self.settings_btn = QPushButton("⚙️ Настройки")
        self.settings_btn.setFixedSize(120, 35)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.settings_btn.clicked.connect(self.open_settings)
        header_layout.addWidget(self.settings_btn)

        main_layout.addLayout(header_layout)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #bdc3c7;")
        main_layout.addWidget(separator)

        # Основной контент
        content_layout = QHBoxLayout()
        content_layout.setSpacing(25)

        # Левая панель - загрузка изображений
        left_panel = self.create_image_panel()
        content_layout.addWidget(left_panel)

        # Правая панель - результаты
        right_panel = self.create_results_panel()
        content_layout.addWidget(right_panel)

        main_layout.addLayout(content_layout)

    def create_image_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #ecf0f1;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок панели
        panel_title = QLabel("Загрузка подписей")
        panel_title.setFont(QFont("Arial", 16, QFont.Bold))
        panel_title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(panel_title)

        # Оригинальная подпись
        orig_section = self.create_image_section("original", "Оригинальная подпись")
        layout.addWidget(orig_section)

        # Проверяемая подпись
        test_section = self.create_image_section("test", "Проверяемая подпись")
        layout.addWidget(test_section)

        # Кнопка проверки
        self.verify_btn = AnimatedButton("🔍 Проверить подписи")
        self.verify_btn.setFixedHeight(50)
        self.verify_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self.verify_btn.setEnabled(False)
        self.verify_btn.setStyleSheet("background-color: #cccccc; color: #666666;")
        self.verify_btn.clicked.connect(self.verify_signatures)
        layout.addWidget(self.verify_btn)

        # Статус загрузки
        self.load_status = QLabel("Загрузите обе подписи для проверки")
        self.load_status.setAlignment(Qt.AlignCenter)
        self.load_status.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(self.load_status)

        return panel

    def create_image_section(self, image_type, title):
        section = QFrame()
        layout = QVBoxLayout(section)
        layout.setSpacing(10)

        # Заголовок секции
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: #34495e;")
        layout.addWidget(title_label)

        # Область для изображения с drag&drop
        image_label = ImageDropLabel("📁 Перетащите сюда изображение\nили нажмите для выбора")
        image_label.mousePressEvent = lambda event, img_type=image_type: self.load_image_dialog(img_type)
        setattr(self, f"{image_type}_image_label", image_label)
        layout.addWidget(image_label)

        # Кнопка загрузки
        btn_layout = QHBoxLayout()

        load_btn = QPushButton("📂 Выбрать файл")
        load_btn.setFixedSize(120, 30)
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        load_btn.clicked.connect(lambda checked, img_type=image_type: self.load_image_dialog(img_type))
        btn_layout.addWidget(load_btn)

        clear_btn = QPushButton("🗑️ Очистить")
        clear_btn.setFixedSize(80, 30)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_btn.clicked.connect(lambda checked, img_type=image_type: self.clear_image(img_type))
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)

        return section

    def create_results_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #ecf0f1;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок результатов
        results_title = QLabel("Результаты проверки")
        results_title.setFont(QFont("Arial", 16, QFont.Bold))
        results_title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(results_title)

        # Индикатор результата
        self.result_frame = QFrame()
        self.result_frame.setFixedHeight(100)
        self.result_frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 10px;
                border: 2px solid #bdc3c7;
            }
        """)
        result_layout = QVBoxLayout(self.result_frame)

        self.result_label = QLabel("Ожидание проверки...")
        self.result_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("color: #7f8c8d;")
        result_layout.addWidget(self.result_label)

        self.result_details = QLabel("Загрузите подписи и нажмите 'Проверить'")
        self.result_details.setAlignment(Qt.AlignCenter)
        self.result_details.setStyleSheet("color: #95a5a6; font-size: 12px;")
        result_layout.addWidget(self.result_details)

        layout.addWidget(self.result_frame)

        # Уверенность системы
        confidence_section = QFrame()
        confidence_layout = QVBoxLayout(confidence_section)

        confidence_header = QLabel("🎯 Уверенность системы")
        confidence_header.setFont(QFont("Arial", 12, QFont.Bold))
        confidence_header.setStyleSheet("color: #34495e;")
        confidence_layout.addWidget(confidence_header)

        self.confidence_bar = QProgressBar()
        self.confidence_bar.setFixedHeight(25)
        self.confidence_bar.setRange(0, 100)
        self.confidence_bar.setValue(0)
        self.confidence_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                text-align: center;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 8px;
            }
        """)
        confidence_layout.addWidget(self.confidence_bar)

        self.confidence_text = QLabel("0%")
        self.confidence_text.setFont(QFont("Arial", 16, QFont.Bold))
        self.confidence_text.setAlignment(Qt.AlignCenter)
        self.confidence_text.setStyleSheet("color: #2c3e50;")
        confidence_layout.addWidget(self.confidence_text)

        layout.addWidget(confidence_section)

        # История проверок
        history_section = QFrame()
        history_layout = QVBoxLayout(history_section)

        history_header = QLabel("📊 История сканирования")
        history_header.setFont(QFont("Arial", 12, QFont.Bold))
        history_header.setStyleSheet("color: #34495e;")
        history_layout.addWidget(history_header)

        # Панель управления историей
        history_controls = QHBoxLayout()

        clear_history_btn = QPushButton("🗑️ Очистить историю")
        clear_history_btn.setFixedSize(140, 30)
        clear_history_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        clear_history_btn.clicked.connect(self.clear_history)
        history_controls.addWidget(clear_history_btn)

        export_btn = QPushButton("💾 Экспорт")
        export_btn.setFixedSize(100, 30)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        export_btn.clicked.connect(self.export_history)
        history_controls.addWidget(export_btn)

        history_layout.addLayout(history_controls)

        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setFixedHeight(200)
        self.history_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                background-color: #f8f9fa;
                font-family: 'Courier New';
                font-size: 11px;
            }
        """)
        history_layout.addWidget(self.history_text)

        layout.addWidget(history_section)

        return panel

    def load_image_dialog(self, image_type):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Выберите {image_type} изображение",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)"
        )

        if file_path:
            self.load_image_from_path(file_path, image_type)

    def load_image_from_path(self, file_path, image_type=None):
        if image_type is None:
            # Определяем тип по текущему состоянию
            if not self.original_path:
                image_type = "original"
            elif not self.test_path:
                image_type = "test"
            else:
                # Если оба загружены, спрашиваем пользователя
                reply = QMessageBox.question(self, "Выбор типа",
                                             "Какую подпись заменить?",
                                             QMessageBox.Yes | QMessageBox.No)
                image_type = "original" if reply == QMessageBox.Yes else "test"

        try:
            image = Image.open(file_path)
            image = ImageOps.fit(image, (300, 200), Image.Resampling.LANCZOS)

            # Конвертация PIL Image в QPixmap
            image = image.convert("RGB")
            data = image.tobytes("raw", "RGB")
            q_image = QImage(data, image.size[0], image.size[1], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)

            image_label = getattr(self, f"{image_type}_image_label")
            image_label.setPixmap(pixmap)
            image_label.setText("")
            image_label.setStyleSheet("border: 2px solid #27ae60; border-radius: 10px;")

            setattr(self, f"{image_type}_path", file_path)

            self.update_verify_button()
            self.update_load_status()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")

    def clear_image(self, image_type):
        image_label = getattr(self, f"{image_type}_image_label")
        image_label.clear()
        image_label.setText("📁 Перетащите сюда изображение\nили нажмите для выбора")
        image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                background-color: #fafafa;
                color: #666666;
                font-size: 14px;
            }
        """)

        setattr(self, f"{image_type}_path", None)
        self.update_verify_button()
        self.update_load_status()

    def update_verify_button(self):
        if self.original_path and self.test_path:
            self.verify_btn.setEnabled(True)
            self.verify_btn.set_color(QColor("#27ae60"))
        else:
            self.verify_btn.setEnabled(False)
            self.verify_btn.setStyleSheet("background-color: #cccccc; color: #666666;")

    def update_load_status(self):
        if self.original_path and self.test_path:
            self.load_status.setText("✓ Обе подписи загружены. Готово к проверке!")
            self.load_status.setStyleSheet("color: #27ae60; font-weight: bold;")
        elif self.original_path:
            self.load_status.setText("⏳ Загружена оригинальная подпись. Загрузите проверяемую.")
            self.load_status.setStyleSheet("color: #f39c12;")
        elif self.test_path:
            self.load_status.setText("⏳ Загружена проверяемая подпись. Загрузите оригинальную.")
            self.load_status.setStyleSheet("color: #f39c12;")
        else:
            self.load_status.setText("Загрузите обе подписи для проверки")
            self.load_status.setStyleSheet("color: #7f8c8d; font-style: italic;")

    def verify_signatures(self):
        if not self.original_path or not self.test_path:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, загрузите обе подписи")
            return

        # Проверка существования файлов
        if not os.path.exists(self.original_path):
            QMessageBox.critical(self, "Ошибка", f"Файл не найден: {self.original_path}")
            return

        if not os.path.exists(self.test_path):
            QMessageBox.critical(self, "Ошибка", f"Файл не найден: {self.test_path}")
            return

        # Проверка существования модели
        if not os.path.exists(self.model_path):
            QMessageBox.critical(self, "Ошибка",
                                 f"Файл модели не найден: {self.model_path}\n"
                                 f"Убедитесь, что модель находится в правильной директории.")
            return

        try:
            # Временно блокируем кнопку
            self.verify_btn.setEnabled(False)
            self.verify_btn.setText("🔍 Проверка...")

            # Вызов функции проверки
            result, confidence = signature_recognition(
                self.original_path,
                self.test_path,
                self.model_path
            )

            # Дополнительная проверка на корректность возвращаемых значений
            if result is None or confidence is None:
                raise ValueError("Функция проверки вернула None значения")

            confidence_percent = confidence * 100

            # Обновление интерфейса
            if result:  # True = оригинал
                result_text = "✅ ПОДЛИННАЯ ПОДПИСЬ"
                result_color = "#27ae60"
                result_details = "Подпись соответствует оригиналу"
            else:  # False = подделка
                result_text = "❌ ПОДДЕЛЬНАЯ ПОДПИСЬ"
                result_color = "#e74c3c"
                result_details = "Подпись не соответствует оригиналу"

            self.result_label.setText(result_text)
            self.result_label.setStyleSheet(f"color: {result_color};")
            self.result_details.setText(result_details)
            self.result_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {result_color}15;
                    border-radius: 10px;
                    border: 2px solid {result_color};
                }}
            """)

            self.confidence_bar.setValue(int(confidence_percent))

            # Цвет прогресс-бара в зависимости от результата
            if confidence_percent >= 80:
                bar_color = "#27ae60"
            elif confidence_percent >= 60:
                bar_color = "#f39c12"
            else:
                bar_color = "#e74c3c"

            self.confidence_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 2px solid #bdc3c7;
                    border-radius: 10px;
                    text-align: center;
                    background-color: #ecf0f1;
                }}
                QProgressBar::chunk {{
                    background-color: {bar_color};
                    border-radius: 8px;
                }}
            """)

            self.confidence_text.setText(f"{confidence_percent:.1f}%")
            self.confidence_text.setStyleSheet(f"color: {bar_color};")

            # Добавление в историю
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            status = "ОРИГИНАЛ" if result else "ПОДДЕЛКА"
            history_entry = f"[{timestamp}] {status} - {confidence_percent:.1f}% уверенности"

            self.verification_history.append(history_entry)
            self.history_text.append(history_entry)

            # Прокрутка к последней записи
            self.history_text.verticalScrollBar().setValue(
                self.history_text.verticalScrollBar().maximum()
            )

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при проверке подписей:\n{str(e)}")
            self.result_label.setText("❌ Ошибка проверки")
            self.result_label.setStyleSheet("color: #e74c3c;")
            self.result_details.setText("Произошла ошибка при анализе подписей")
            self.confidence_bar.setValue(0)
            self.confidence_text.setText("0%")

        finally:
            # Восстанавливаем кнопку
            self.verify_btn.setEnabled(True)
            self.verify_btn.setText("🔍 Проверить подписи")
            self.verify_btn.set_color(QColor("#27ae60"))

    def clear_history(self):
        reply = QMessageBox.question(self, "Очистка истории",
                                     "Вы уверены, что хотите очистить историю проверок?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.history_text.clear()
            self.verification_history.clear()
            self.history_text.append("История очищена")

    def export_history(self):
        if not self.verification_history:
            QMessageBox.information(self, "Экспорт", "История проверок пуста")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт истории проверок",
            "signature_verification_history.txt",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("История проверок подписей\n")
                    f.write("=" * 30 + "\n\n")
                    for entry in self.verification_history:
                        f.write(entry + "\n")

                QMessageBox.information(self, "Успех", f"История экспортирована в:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать историю:\n{str(e)}")

    def open_settings(self):
        settings_dialog = SettingsDialog(self, self.threshold)
        if settings_dialog.exec():
            self.threshold = settings_dialog.get_threshold()
            QMessageBox.information(self, "Настройки", f"Порог проверки установлен: {self.threshold}%")


class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_threshold=70):
        super().__init__(parent)
        self.threshold = current_threshold
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("⚙️ Настройки системы")
        self.setFixedSize(450, 350)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)

        # Заголовок
        title_label = QLabel("Настройки системы")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Порог проверки
        threshold_group = QFrame()
        threshold_layout = QVBoxLayout(threshold_group)

        threshold_label = QLabel("🎯 Порог оригинальности подписи")
        threshold_label.setFont(QFont("Arial", 12, QFont.Bold))
        threshold_label.setStyleSheet("color: #34495e;")
        threshold_layout.addWidget(threshold_label)

        # Слайдер и значение
        slider_layout = QHBoxLayout()

        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(50, 95)
        self.threshold_slider.setValue(self.threshold)
        self.threshold_slider.valueChanged.connect(self.update_threshold_label)
        self.threshold_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 8px;
                background: #ecf0f1;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 2px solid #2980b9;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
        slider_layout.addWidget(self.threshold_slider)

        self.threshold_value = QLabel(f"{self.threshold}%")
        self.threshold_value.setFont(QFont("Arial", 14, QFont.Bold))
        self.threshold_value.setFixedWidth(50)
        self.threshold_value.setStyleSheet("color: #3498db;")
        self.threshold_value.setAlignment(Qt.AlignCenter)
        slider_layout.addWidget(self.threshold_value)

        threshold_layout.addLayout(slider_layout)

        # Пояснение
        explanation = QLabel("Подписи с уверенностью выше этого порога считаются подлинными")
        explanation.setStyleSheet("color: #7f8c8d; font-size: 11px; font-style: italic;")
        explanation.setWordWrap(True)
        threshold_layout.addWidget(explanation)

        layout.addWidget(threshold_group)

        # Дополнительные настройки
        advanced_group = QFrame()
        advanced_layout = QVBoxLayout(advanced_group)

        advanced_label = QLabel("🔧 Дополнительные настройки")
        advanced_label.setFont(QFont("Arial", 12, QFont.Bold))
        advanced_label.setStyleSheet("color: #34495e;")
        advanced_layout.addWidget(advanced_label)

        # Чекбоксы
        self.auto_save_check = QCheckBox("Автоматически сохранять результаты")
        self.auto_save_check.setChecked(True)

        self.show_details_check = QCheckBox("Показывать детальную информацию")
        self.show_details_check.setChecked(True)

        advanced_layout.addWidget(self.auto_save_check)
        advanced_layout.addWidget(self.show_details_check)

        layout.addWidget(advanced_group)

        layout.addStretch()

        # Кнопки
        button_layout = QHBoxLayout()

        ok_btn = QPushButton("✅ Применить")
        ok_btn.setFixedHeight(40)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def update_threshold_label(self, value):
        self.threshold = value
        self.threshold_value.setText(f"{value}%")

    def get_threshold(self):
        return self.threshold
