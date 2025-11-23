import os
import json
import time
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                               QPushButton, QLabel, QTextEdit, QMessageBox,
                               QListWidgetItem, QFileDialog, QGroupBox, QSplitter,
                               QApplication)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor


class HistoryTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.history_file = "processing_history.json"
        self.history_data = []
        self.setup_ui()
        self.load_history()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок
        title_label = QLabel("История обработки")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Кнопки управления
        buttons_layout = QHBoxLayout()

        self.clear_history_btn = QPushButton("Очистить историю")
        self.clear_history_btn.clicked.connect(self.clear_history)
        buttons_layout.addWidget(self.clear_history_btn)

        self.export_btn = QPushButton("Экспорт истории")
        self.export_btn.clicked.connect(self.export_history)
        buttons_layout.addWidget(self.export_btn)

        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.load_history)
        buttons_layout.addWidget(self.refresh_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Splitter для разделения списка и деталей
        splitter = QSplitter(Qt.Horizontal)

        # Левая панель - список истории
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        list_label = QLabel("Записи истории:")
        list_label.setFont(QFont("Arial", 10, QFont.Bold))
        left_layout.addWidget(list_label)

        # Список истории
        self.history_list = QListWidget()
        self.history_list.itemSelectionChanged.connect(self.show_history_details)
        left_layout.addWidget(self.history_list)

        # Правая панель - детали
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        details_label = QLabel("Детали обработки:")
        details_label.setFont(QFont("Arial", 10, QFont.Bold))
        right_layout.addWidget(details_label)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        right_layout.addWidget(self.details_text)

        # Кнопки для деталей
        details_buttons_layout = QHBoxLayout()
        self.copy_details_btn = QPushButton("Копировать детали")
        self.copy_details_btn.clicked.connect(self.copy_details)
        self.copy_details_btn.setEnabled(False)
        details_buttons_layout.addWidget(self.copy_details_btn)

        self.delete_entry_btn = QPushButton("Удалить запись")
        self.delete_entry_btn.clicked.connect(self.delete_selected_entry)
        self.delete_entry_btn.setEnabled(False)
        details_buttons_layout.addWidget(self.delete_entry_btn)

        details_buttons_layout.addStretch()
        right_layout.addLayout(details_buttons_layout)

        # Добавляем виджеты в splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])

        layout.addWidget(splitter)

        # Статистика
        self.stats_label = QLabel("Всего записей: 0")
        self.stats_label.setStyleSheet("color: #cccccc; font-size: 11px; padding: 5px;")
        layout.addWidget(self.stats_label)

    def load_history(self):
        """Загрузка истории из файла"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history_data = json.load(f)
            else:
                self.history_data = []

            self.update_history_display()

        except Exception as e:
            self.show_error(f"Ошибка загрузки истории: {e}")

    def save_history(self):
        """Сохранение истории в файл"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.show_error(f"Ошибка сохранения истории: {e}")

    def add_to_history(self, image_path, result, processing_type="Обработка"):
        """Добавление записи в историю"""
        try:
            # Если image_path - это строка сравнения (для верификации)
            if " vs " in str(image_path):
                image_name = str(image_path)
            else:
                image_name = os.path.basename(image_path) if image_path else "Неизвестный файл"

            history_entry = {
                'id': len(self.history_data) + 1,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'image_name': image_name,
                'image_path': image_path,
                'processing_type': processing_type,
                'result_preview': result[:100] + "..." if len(result) > 100 else result,
                'full_result': result
            }

            self.history_data.append(history_entry)
            self.save_history()
            self.update_history_display()

            self.main_window.update_status(f"Запись добавлена в историю: {processing_type}")

        except Exception as e:
            print(f"Ошибка добавления в историю: {e}")

    def update_history_display(self):
        """Обновление отображения списка истории"""
        self.history_list.clear()

        for entry in reversed(self.history_data):  # Показываем новые записи первыми
            item_text = f"{entry['timestamp']} - {entry['image_name']} ({entry['processing_type']})"
            item = QListWidgetItem(item_text)

            # Цвет в зависимости от типа обработки
            if entry['processing_type'] == "Анализ подписи":
                item.setForeground(QColor("#3498db"))  # Синий
            elif entry['processing_type'] == "Верификация":
                item.setForeground(QColor("#e74c3c"))  # Красный
            else:
                item.setForeground(QColor("#ffffff"))  # Белый

            self.history_list.addItem(item)

        self.stats_label.setText(f"Всего записей: {len(self.history_data)}")

    def show_history_details(self):
        """Показ деталей выбранной записи"""
        current_row = self.history_list.currentRow()
        if current_row >= 0 and self.history_data:
            # Преобразуем индекс т.к. список отображается в обратном порядке
            actual_index = len(self.history_data) - 1 - current_row
            entry = self.history_data[actual_index]

            details = f"""ЗАПИСЬ ИСТОРИИ #{entry['id']}

ВРЕМЯ: {entry['timestamp']}
ТИП ОБРАБОТКИ: {entry['processing_type']}
ФАЙЛ: {entry['image_name']}

РЕЗУЛЬТАТ:
{entry['full_result']}"""

            self.details_text.setText(details)
            self.copy_details_btn.setEnabled(True)
            self.delete_entry_btn.setEnabled(True)
        else:
            self.details_text.clear()
            self.copy_details_btn.setEnabled(False)
            self.delete_entry_btn.setEnabled(False)

    def clear_history(self):
        """Очистка всей истории"""
        reply = QMessageBox.question(self, "Подтверждение",
                                     "Вы уверены, что хотите очистить всю историю?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.history_data = []
            self.save_history()
            self.update_history_display()
            self.details_text.clear()
            self.main_window.update_status("История очищена")

    def export_history(self):
        """Экспорт истории в файл"""
        if not self.history_data:
            self.show_error("История пуста")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт истории",
            f"history_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.history_data, f, ensure_ascii=False, indent=2)
                self.main_window.update_status(f"История экспортирована в {os.path.basename(file_path)}")
                QMessageBox.information(self, "Успех", "История успешно экспортирована")
            except Exception as e:
                self.show_error(f"Ошибка экспорта: {e}")

    def copy_details(self):
        """Копирование деталей в буфер обмена"""
        text = self.details_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.main_window.update_status("Детали скопированы в буфер обмена")

    def delete_selected_entry(self):
        """Удаление выбранной записи"""
        current_row = self.history_list.currentRow()
        if current_row >= 0 and self.history_data:
            actual_index = len(self.history_data) - 1 - current_row
            entry = self.history_data[actual_index]

            reply = QMessageBox.question(self, "Подтверждение",
                                         f"Удалить запись от {entry['timestamp']}?",
                                         QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                del self.history_data[actual_index]
                self.save_history()
                self.update_history_display()
                self.details_text.clear()
                self.main_window.update_status("Запись удалена из истории")

    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)
        self.main_window.update_status(f"Ошибка: {message}")
