import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTextEdit, QMessageBox, QFileDialog,
                               QGroupBox, QProgressBar, QFrame, QApplication)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QPixmap, QFont, QColor
from .widgets import DragDropLabel
from .model_handler import SignatureAnalyzer


class VerificationWorker(QThread):
    finished = Signal(dict)
    progress = Signal(str)
    error = Signal(str)

    def __init__(self, image1_path, image2_path, model_handler):
        super().__init__()
        self.image1_path = image1_path
        self.image2_path = image2_path
        self.model_handler = model_handler

    def run(self):
        try:
            self.progress.emit("Начало сравнения подписей...")

            self.progress.emit("Анализ эталонной подписи...")

            self.progress.emit("Анализ проверяемой подписи...")

            self.progress.emit("Сравнение характеристик...")

            # Реальное сравнение с помощью модели
            comparison_result = self.model_handler.compare_signatures(
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
        self.model_handler = SignatureAnalyzer()  # Без передачи пути - автопоиск
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок
        title_label = QLabel("Верификация подписей")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        description = QLabel("Сравните две подписи для проверки их подлинности и схожести")
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("color: #cccccc;")
        layout.addWidget(description)

        # Группа для двух изображений
        images_group = QGroupBox("Сравниваемые подписи")
        images_layout = QHBoxLayout(images_group)

        # Эталонная подпись
        reference_frame = QFrame()
        reference_layout = QVBoxLayout(reference_frame)

        reference_label = QLabel("Эталонная подпись")
        reference_label.setAlignment(Qt.AlignCenter)
        reference_label.setFont(QFont("Arial", 10, QFont.Bold))
        reference_layout.addWidget(reference_label)

        self.reference_drop = DragDropLabel("Перетащите эталонную подпись")
        self.reference_drop.image_dropped.connect(lambda path: self.load_reference_image(path))
        reference_layout.addWidget(self.reference_drop)

        reference_btn = QPushButton("Выбрать эталон")
        reference_btn.clicked.connect(self.select_reference_image)
        reference_layout.addWidget(reference_btn)

        # Проверяемая подпись
        verify_frame = QFrame()
        verify_layout = QVBoxLayout(verify_frame)

        verify_label = QLabel("Проверяемая подпись")
        verify_label.setAlignment(Qt.AlignCenter)
        verify_label.setFont(QFont("Arial", 10, QFont.Bold))
        verify_layout.addWidget(verify_label)

        self.verify_drop = DragDropLabel("Перетащите проверяемую подпись")
        self.verify_drop.image_dropped.connect(lambda path: self.load_verify_image(path))
        verify_layout.addWidget(self.verify_drop)

        verify_btn = QPushButton("Выбрать для проверки")
        verify_btn.clicked.connect(self.select_verify_image)
        verify_layout.addWidget(verify_btn)

        images_layout.addWidget(reference_frame)
        images_layout.addWidget(verify_frame)
        layout.addWidget(images_group)

        # Группа верификации
        verify_group = QGroupBox("Верификация")
        verify_layout = QVBoxLayout(verify_group)

        info_label = QLabel("Сравнение выполняется с помощью нейросетевой модели, анализирующей стиль написания")
        info_label.setStyleSheet("color: #cccccc; font-size: 11px; padding: 5px;")
        info_label.setWordWrap(True)
        verify_layout.addWidget(info_label)

        self.verify_btn = QPushButton("Начать верификацию")
        self.verify_btn.clicked.connect(self.verify_signatures)
        self.verify_btn.setEnabled(False)
        verify_layout.addWidget(self.verify_btn)

        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        verify_layout.addWidget(self.progress_bar)

        # Статус
        self.status_label = QLabel("Загрузите обе подписи для верификации")
        self.status_label.setStyleSheet("color: #cccccc; font-size: 11px; padding: 5px;")
        verify_layout.addWidget(self.status_label)

        layout.addWidget(verify_group)

        # Группа результатов
        result_group = QGroupBox("Результаты верификации")
        result_layout = QVBoxLayout(result_group)

        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("Результаты сравнения подписей появятся здесь...")
        self.result_text.setMinimumHeight(200)
        result_layout.addWidget(self.result_text)

        layout.addWidget(result_group)

        layout.addStretch()

    def select_reference_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите эталонную подпись",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)"
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
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)"
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
            self.verify_image_path,
            self.model_handler
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_verification_finished)
        self.worker.error.connect(self.on_verification_error)
        self.worker.start()

    def update_progress(self, message):
        self.status_label.setText(message)
        self.main_window.update_status(message)

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

        # Подсвечиваем кнопку в зависимости от результата
        similarity = result.get('raw_similarity', 0.5)
        if similarity > 0.7:
            self.verify_btn.setStyleSheet("background-color: #27ae60; color: white;")
        elif similarity > 0.5:
            self.verify_btn.setStyleSheet("background-color: #f39c12; color: white;")
        else:
            self.verify_btn.setStyleSheet("background-color: #e74c3c; color: white;")

        self.main_window.update_status("Верификация завершена")

    def on_verification_error(self, error_message):
        self.show_error(f"Ошибка верификации: {error_message}")
        self.verify_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ошибка верификации")
        self.verify_btn.setStyleSheet("")  # Сбрасываем стиль

    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)
        self.main_window.update_status(f"Ошибка: {message}")
