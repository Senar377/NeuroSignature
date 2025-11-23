import os
import time
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTextEdit, QProgressBar, QMessageBox,
                               QFileDialog, QGroupBox, QApplication)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QPixmap, QFont
from .widgets import DragDropLabel
from .model_handler import SignatureAnalyzer


class ProcessingWorker(QThread):
    finished = Signal(dict)
    progress = Signal(str)
    error = Signal(str)

    def __init__(self, image_path, model_handler):
        super().__init__()
        self.image_path = image_path
        self.model_handler = model_handler

    def run(self):
        try:
            self.progress.emit("Анализ качества подписи...")
            time.sleep(0.5)

            self.progress.emit("Извлечение характеристик...")
            time.sleep(0.5)

            # Реальный анализ с помощью модели
            analysis_result = self.model_handler.analyze_single_signature(self.image_path)

            self.progress.emit("Формирование отчета...")
            time.sleep(0.5)

            # Генерация детального отчета
            result_text = self._generate_analysis_report(analysis_result)

            self.progress.emit("Анализ завершен")
            self.finished.emit({
                'text': result_text,
                'analysis': analysis_result
            })

        except Exception as e:
            self.error.emit(f"Ошибка обработки: {str(e)}")

    def _generate_analysis_report(self, analysis: dict) -> str:
        """Генерация детального отчета анализа"""
        report = f"АНАЛИЗ ПОДПИСИ\n"
        report += "=" * 50 + "\n\n"

        report += f"Файл: {os.path.basename(self.image_path)}\n"
        report += f"Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        report += "ОСНОВНЫЕ ХАРАКТЕРИСТИКИ:\n"
        report += f"• Подлинность: {'ПОДЛИННАЯ' if analysis['is_genuine'] else 'ПОДДЕЛЬНАЯ'}\n"
        report += f"• Уверенность анализа: {analysis['confidence']:.1%}\n"
        report += f"• Общее качество: {analysis['quality_score']:.1%}\n"
        report += f"• Четкость подписи: {analysis['clarity']:.1%}\n"
        report += f"• Интенсивность нажима: {analysis['pressure']:.1%}\n"
        report += f"• Угол наклона: {analysis['slant']:.1f}°\n"
        report += f"• Согласованность линий: {analysis['consistency']:.1%}\n\n"

        # Оценка качества
        quality_score = (analysis['clarity'] + analysis['consistency'] + analysis['pressure']) / 3
        if quality_score > 0.8:
            quality_verdict = "ОТЛИЧНОЕ"
        elif quality_score > 0.6:
            quality_verdict = "ХОРОШЕЕ"
        elif quality_score > 0.4:
            quality_verdict = "УДОВЛЕТВОРИТЕЛЬНОЕ"
        else:
            quality_verdict = "НИЗКОЕ"

        report += f"ОБЩАЯ ОЦЕНКА КАЧЕСТВА: {quality_verdict}\n"
        report += f"Итоговый балл: {quality_score:.1%}\n\n"

        # Рекомендации
        report += "РЕКОМЕНДАЦИИ:\n"
        if analysis['clarity'] < 0.6:
            report += "• Подпись имеет низкую четкость\n"
        if analysis['pressure'] < 0.5:
            report += "• Слабый нажим, рекомендуется более уверенное написание\n"
        if analysis['consistency'] < 0.7:
            report += "• Наблюдается нестабильность в начертании\n"

        if quality_score > 0.7:
            report += "• Подпись соответствует стандартам качества\n"

        if not analysis.get('features_extracted', True):
            report += "\n⚠ Внимание: анализ выполнен с ограниченной точностью\n"

        return report


class ProcessingTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_image_path = None
        self.worker = None
        self.model_handler = SignatureAnalyzer()  # Без передачи пути - автопоиск
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Группа загрузки изображения
        image_group = QGroupBox("Загрузка изображения подписи")
        image_layout = QVBoxLayout(image_group)

        self.drop_label = DragDropLabel("Перетащите изображение подписи сюда")
        self.drop_label.image_dropped.connect(self.load_image)
        image_layout.addWidget(self.drop_label)

        # Кнопка выбора файла
        file_buttons_layout = QHBoxLayout()
        self.select_file_btn = QPushButton("Выбрать файл")
        self.select_file_btn.clicked.connect(self.select_image_file)
        file_buttons_layout.addWidget(self.select_file_btn)

        self.clear_image_btn = QPushButton("Очистить")
        self.clear_image_btn.clicked.connect(self.clear_image)
        self.clear_image_btn.setEnabled(False)
        file_buttons_layout.addWidget(self.clear_image_btn)

        file_buttons_layout.addStretch()
        image_layout.addLayout(file_buttons_layout)
        layout.addWidget(image_group)

        # Группа обработки
        process_group = QGroupBox("Анализ подписи")
        process_layout = QVBoxLayout(process_group)

        info_label = QLabel("Анализ определяет: качество, четкость, нажим, угол наклона и подлинность подписи")
        info_label.setStyleSheet("color: #cccccc; font-size: 11px; padding: 5px;")
        info_label.setWordWrap(True)
        process_layout.addWidget(info_label)

        self.process_btn = QPushButton("Начать анализ")
        self.process_btn.clicked.connect(self.process_image)
        self.process_btn.setEnabled(False)
        process_layout.addWidget(self.process_btn)

        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        process_layout.addWidget(self.progress_bar)

        # Статус обработки
        self.status_label = QLabel("Загрузите изображение подписи для анализа")
        self.status_label.setStyleSheet("color: #cccccc; font-size: 11px; padding: 5px;")
        process_layout.addWidget(self.status_label)

        layout.addWidget(process_group)

        # Группа результатов
        result_group = QGroupBox("Результаты анализа")
        result_layout = QVBoxLayout(result_group)

        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("Здесь появится детальный анализ подписи...")
        self.result_text.setMinimumHeight(250)
        result_layout.addWidget(self.result_text)

        # Кнопки результатов
        result_buttons_layout = QHBoxLayout()
        self.copy_btn = QPushButton("Копировать отчет")
        self.copy_btn.clicked.connect(self.copy_text)
        self.copy_btn.setEnabled(False)
        result_buttons_layout.addWidget(self.copy_btn)

        self.save_btn = QPushButton("Сохранить отчет")
        self.save_btn.clicked.connect(self.save_text)
        self.save_btn.setEnabled(False)
        result_buttons_layout.addWidget(self.save_btn)

        result_buttons_layout.addStretch()
        result_layout.addLayout(result_buttons_layout)
        layout.addWidget(result_group)

        layout.addStretch()

    def select_image_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение подписи",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)"
        )
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        try:
            self.drop_label.set_image(file_path)
            self.current_image_path = file_path
            self.process_btn.setEnabled(True)
            self.clear_image_btn.setEnabled(True)
            self.status_label.setText(f"Изображение загружено: {os.path.basename(file_path)}")
            self.main_window.update_status(f"Изображение загружено: {os.path.basename(file_path)}")

            # Очищаем предыдущие результаты
            self.result_text.clear()
            self.copy_btn.setEnabled(False)
            self.save_btn.setEnabled(False)

        except Exception as e:
            self.show_error(f"Ошибка загрузки изображения: {str(e)}")

    def clear_image(self):
        self.drop_label.clear_image()
        self.current_image_path = None
        self.process_btn.setEnabled(False)
        self.clear_image_btn.setEnabled(False)
        self.result_text.clear()
        self.status_label.setText("Загрузите изображение подписи для анализа")
        self.copy_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.main_window.update_status("Изображение очищено")

    def process_image(self):
        if not self.current_image_path:
            self.show_error("Сначала загрузите изображение")
            return

        if self.worker and self.worker.isRunning():
            self.show_error("Анализ уже выполняется")
            return

        self.process_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Начало анализа...")
        self.result_text.clear()

        self.worker = ProcessingWorker(self.current_image_path, self.model_handler)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.error.connect(self.on_processing_error)
        self.worker.start()

    def update_progress(self, message):
        self.status_label.setText(message)
        self.main_window.update_status(message)

    def on_processing_finished(self, result):
        self.result_text.setText(result['text'])
        self.copy_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.process_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Анализ завершен успешно")

        # Добавляем в историю
        if hasattr(self.main_window, 'history_tab'):
            self.main_window.history_tab.add_to_history(
                self.current_image_path,
                result['text'],
                "Анализ подписи"
            )

        self.main_window.update_status("Анализ завершен")

    def on_processing_error(self, error_message):
        self.show_error(f"Ошибка анализа: {error_message}")
        self.process_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ошибка анализа")
        self.main_window.update_status("Ошибка анализа")

    def copy_text(self):
        text = self.result_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_label.setText("Отчет скопирован в буфер обмена")
            self.main_window.update_status("Отчет скопирован")

    def save_text(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчет анализа",
            f"анализ_подписи_{time.strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.result_text.toPlainText())
                self.status_label.setText(f"Отчет сохранен в {os.path.basename(file_path)}")
                self.main_window.update_status(f"Отчет сохранен в {os.path.basename(file_path)}")
            except Exception as e:
                self.show_error(f"Ошибка сохранения: {str(e)}")

    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)
        self.main_window.update_status(f"Ошибка: {message}")
