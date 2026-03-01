# Gui/verification_tab.py
import os
import random
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTextEdit, QMessageBox, QFileDialog,
                               QGroupBox, QProgressBar, QFrame, QApplication,
                               QScrollArea, QSizePolicy, QDialog)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QPixmap, QFont, QColor
from .widgets import DragDropLabel
from .model_handler import model_handler


class VerificationWorker(QThread):
    finished = Signal(dict)
    progress = Signal(str)
    error = Signal(str)

    def __init__(self, image1_path, image2_path):
        super().__init__()
        self.image1_path = image1_path
        self.image2_path = image2_path

    def run(self):
        try:
            self.progress.emit("Начало сравнения подписей...")
            comparison_result = model_handler.compare_signatures(
                self.image1_path,
                self.image2_path
            )
            self.progress.emit("Формирование результата...")
            self.finished.emit(comparison_result)
        except Exception as e:
            self.error.emit(f"Ошибка верификации: {str(e)}")


class VerificationTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.reference_image_path = None
        self.verify_image_path = None
        self.worker = None
        self.current_theme = "light"
        self.secret_clicks = 0
        self.last_click_pos = None
        self.setup_ui()
        self.setup_easter_egg_detection()

    def setup_ui(self):
        # Основной layout с возможностью прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll_widget = QWidget()
        self.main_layout = QVBoxLayout(scroll_widget)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок
        self.title_label = QLabel("Верификация подписей")
        self.title_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        description = QLabel("Сравните две подписи для проверки их подлинности и схожести")
        description.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(description)

        # Группа для двух изображений с гибкой версткой
        self.images_group = QGroupBox("Сравниваемые подписи")
        images_layout = QHBoxLayout(self.images_group)
        images_layout.setSpacing(15)

        # Эталонная подпись
        reference_frame = QFrame()
        reference_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        reference_layout = QVBoxLayout(reference_frame)
        reference_layout.setSpacing(5)

        reference_label = QLabel("Эталонная подпись")
        reference_label.setAlignment(Qt.AlignCenter)
        reference_label.setFont(QFont("Arial", 10, QFont.Bold))
        reference_layout.addWidget(reference_label)

        self.reference_drop = DragDropLabel("Перетащите эталонную подпись")
        self.reference_drop.image_dropped.connect(self.load_reference_image)
        self.reference_drop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        reference_layout.addWidget(self.reference_drop, 1)

        reference_btn = QPushButton("Выбрать эталон")
        reference_btn.clicked.connect(self.select_reference_image)
        reference_btn.setFixedHeight(35)
        reference_layout.addWidget(reference_btn)

        # Проверяемая подпись
        verify_frame = QFrame()
        verify_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        verify_layout = QVBoxLayout(verify_frame)
        verify_layout.setSpacing(5)

        verify_label = QLabel("Проверяемая подпись")
        verify_label.setAlignment(Qt.AlignCenter)
        verify_label.setFont(QFont("Arial", 10, QFont.Bold))
        verify_layout.addWidget(verify_label)

        self.verify_drop = DragDropLabel("Перетащите проверяемую подпись")
        self.verify_drop.image_dropped.connect(self.load_verify_image)
        self.verify_drop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        verify_layout.addWidget(self.verify_drop, 1)

        verify_btn = QPushButton("Выбрать для проверки")
        verify_btn.clicked.connect(self.select_verify_image)
        verify_btn.setFixedHeight(35)
        verify_layout.addWidget(verify_btn)

        images_layout.addWidget(reference_frame, 1)
        images_layout.addWidget(verify_frame, 1)
        self.main_layout.addWidget(self.images_group, 2)

        # Группа верификации
        self.verify_group = QGroupBox("Верификация")
        verify_layout = QVBoxLayout(self.verify_group)

        info_label = QLabel("Сравнение выполняется с помощью нейросетевой модели, анализирующей стиль написания")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 11px; padding: 5px;")
        verify_layout.addWidget(info_label)

        self.verify_btn = QPushButton("Начать верификацию")
        self.verify_btn.clicked.connect(self.verify_signatures)
        self.verify_btn.setEnabled(False)
        self.verify_btn.setFixedHeight(40)
        verify_layout.addWidget(self.verify_btn)

        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setFixedHeight(20)
        verify_layout.addWidget(self.progress_bar)

        # Статус
        self.status_label = QLabel("Загрузите обе подписи для верификации")
        self.status_label.setWordWrap(True)
        verify_layout.addWidget(self.status_label)

        self.main_layout.addWidget(self.verify_group, 0)

        # Группа результатов
        self.result_group = QGroupBox("Результаты верификации")
        result_layout = QVBoxLayout(self.result_group)

        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("Результаты сравнения подписей появятся здесь...")
        self.result_text.setMinimumHeight(150)
        result_layout.addWidget(self.result_text)

        self.main_layout.addWidget(self.result_group, 1)

        self.main_layout.addStretch()

        scroll_area.setWidget(scroll_widget)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

    def setup_easter_egg_detection(self):
        """Настройка обнаружения пасхалок"""
        self.easter_egg_timer = QTimer()
        self.easter_egg_timer.setSingleShot(True)
        self.easter_egg_timer.timeout.connect(self.reset_secret_clicks)

    def reset_secret_clicks(self):
        """Сброс счетчика секретных кликов"""
        self.secret_clicks = 0

    def mousePressEvent(self, event):
        """Отслеживание специальных кликов"""
        super().mousePressEvent(event)

        # Проверяем клик по заголовку
        if self.title_label.geometry().contains(event.pos()):
            self.secret_clicks += 1
            self.easter_egg_timer.start(3000)  # 3 секунды на последовательность

            if self.secret_clicks == 7:  # 7 кликов по заголовку
                self.show_secret_message()
                self.secret_clicks = 0
                self.easter_egg_timer.stop()
            elif self.secret_clicks > 0 and self.secret_clicks < 7:
                self.main_window.statusBar().showMessage(
                    f"🎯 Секретная комбинация: {self.secret_clicks}/7"
                )

    def show_secret_message(self):
        """Показ секретного сообщения"""
        dialog = QDialog(self)
        dialog.setWindowTitle("🎯 СЕКРЕТ РАЗРАБОТЧИКА")
        dialog.setFixedSize(400, 300)

        layout = QVBoxLayout(dialog)

        messages = [
            "Знаете ли вы?\n\nКашапов Арсен создал эту программу за 3 месяца!",
            "Интересный факт:\n\nНейросеть обучалась на 10,000 подписей!",
            "Секретно:\n\nВерсия 3.0 уже в разработке!",
            "Пасхалка:\n\nПопробуйте нажать Ctrl+Shift+K в главном окне!",
            "Факт:\n\nТочность модели - 94.7%!",
        ]

        label = QLabel(random.choice(messages))
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 12))
        label.setStyleSheet("color: #3498db; padding: 20px;")
        layout.addWidget(label)

        close_btn = QPushButton("👍 Круто!")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec_()

    def select_reference_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите эталонную подпись",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.gif *.webp);;All Files (*)"
        )
        if file_path:
            self.load_reference_image(file_path)

    def load_reference_image(self, file_path):
        try:
            self.reference_drop.set_image(file_path)
            self.reference_image_path = file_path
            self.check_ready_state()
            self.status_label.setText(f"Эталон загружен: {os.path.basename(file_path)}")
        except Exception as e:
            self.show_error(f"Ошибка загрузки эталона: {str(e)}")

    def select_verify_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите проверяемую подпись",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.gif *.webp);;All Files (*)"
        )
        if file_path:
            self.load_verify_image(file_path)

    def load_verify_image(self, file_path):
        try:
            self.verify_drop.set_image(file_path)
            self.verify_image_path = file_path
            self.check_ready_state()
            self.status_label.setText(f"Проверяемая подпись загружена: {os.path.basename(file_path)}")
        except Exception as e:
            self.show_error(f"Ошибка загрузки проверяемой подписи: {str(e)}")

    def check_ready_state(self):
        if self.reference_image_path and self.verify_image_path:
            self.verify_btn.setEnabled(True)
            self.status_label.setText("Готово к верификации")
        else:
            self.verify_btn.setEnabled(False)

    def verify_signatures(self):
        if not self.reference_image_path or not self.verify_image_path:
            self.show_error("Загрузите обе подписи для верификации")
            return

        if self.worker and self.worker.isRunning():
            self.show_error("Верификация уже выполняется")
            return

        self.verify_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Начало верификации...")
        self.result_text.clear()

        self.worker = VerificationWorker(
            self.reference_image_path,
            self.verify_image_path
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_verification_finished)
        self.worker.error.connect(self.on_verification_error)
        self.worker.start()

    def update_progress(self, message):
        self.status_label.setText(message)
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(message)

    def on_verification_finished(self, result):
        self.verify_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        # Форматируем результат
        result_text = f"РЕЗУЛЬТАТ ВЕРИФИКАЦИИ\n"
        result_text += "=" * 50 + "\n\n"

        result_text += f"ВЕРДИКТ: {result['verdict']}\n"
        result_text += f"СТЕПЕНЬ СХОДСТВА: {result['similarity']:.1f}%\n"
        result_text += f"УВЕРЕННОСТЬ: {result['confidence_level']}\n\n"

        result_text += result['details']

        self.result_text.setText(result_text)
        self.status_label.setText("Верификация завершена")

        # Добавляем в историю
        if hasattr(self.main_window, 'history_tab'):
            history_text = f"Верификация: {result['similarity']:.1f}% схожести - {result['verdict']}"
            self.main_window.history_tab.add_to_history(
                f"{os.path.basename(self.reference_image_path)} vs {os.path.basename(self.verify_image_path)}",
                result_text,
                "Верификация"
            )

        similarity = result.get('raw_similarity', 0.5)
        if similarity > 0.7:
            self.verify_btn.setStyleSheet("background-color: #27ae60; color: white;")
        elif similarity > 0.5:
            self.verify_btn.setStyleSheet("background-color: #f39c12; color: white;")
        else:
            self.verify_btn.setStyleSheet("background-color: #e74c3c; color: white;")

        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage("Верификация завершена")

    def on_verification_error(self, error_message):
        self.show_error(f"Ошибка верификации: {error_message}")
        self.verify_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ошибка верификации")
        self.verify_btn.setStyleSheet("")

    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(f"Ошибка: {message}")

    def update_theme(self, theme):
        """Обновление темы для всех элементов"""
        self.current_theme = theme
        self.reference_drop.set_theme(theme)
        self.verify_drop.set_theme(theme)

        if theme == "dark":
            self.status_label.setStyleSheet("color: #cccccc; font-size: 11px; padding: 5px;")
        else:
            self.status_label.setStyleSheet("color: #666666; font-size: 11px; padding: 5px;")

    def on_window_resized(self):
        """Обработка изменения размера окна"""
        if self.reference_image_path:
            self.reference_drop.set_image(self.reference_image_path)
        if self.verify_image_path:
            self.verify_drop.set_image(self.verify_image_path)