from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QPushButton, QGroupBox, QMessageBox)
from PySide6.QtCore import Qt
import json
import os
from datetime import datetime


class HistoryWidget(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.history_file = "scan_history.json"
        self.init_ui()
        self.load_history()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Заголовок
        title = QLabel("История проверок")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Панель управления
        control_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.load_history)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        control_layout.addWidget(refresh_btn)

        clear_btn = QPushButton("🗑️ Очистить историю")
        clear_btn.clicked.connect(self.clear_history)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        control_layout.addWidget(clear_btn)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # Таблица истории
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "Дата", "Оригинальная подпись", "Проверяемая подпись",
            "Результат", "Уверенность"
        ])

        # Настройка таблицы
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        layout.addWidget(self.history_table)

    def load_history(self):
        """Загрузка истории из файла"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
            else:
                history_data = []

            self.populate_table(history_data)

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить историю: {str(e)}")

    def populate_table(self, history_data):
        """Заполнение таблицы данными"""
        self.history_table.setRowCount(len(history_data))

        for row, record in enumerate(history_data):
            # Дата
            date_item = QTableWidgetItem(record.get('timestamp', ''))
            self.history_table.setItem(row, 0, date_item)

            # Имена файлов
            orig_item = QTableWidgetItem(os.path.basename(record.get('original_path', '')))
            test_item = QTableWidgetItem(os.path.basename(record.get('test_path', '')))
            self.history_table.setItem(row, 1, orig_item)
            self.history_table.setItem(row, 2, test_item)

            # Результат
            result = record.get('result', False)
            result_text = "Оригинал" if result else "Подделка"
            result_item = QTableWidgetItem(result_text)
            result_item.setForeground(Qt.green if result else Qt.red)
            self.history_table.setItem(row, 3, result_item)

            # Уверенность
            confidence = record.get('confidence', 0)
            confidence_item = QTableWidgetItem(f"{confidence * 100:.2f}%")
            self.history_table.setItem(row, 4, confidence_item)

    def clear_history(self):
        """Очистка истории"""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите очистить всю историю?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                if os.path.exists(self.history_file):
                    os.remove(self.history_file)
                self.history_table.setRowCount(0)
                QMessageBox.information(self, "Успех", "История очищена!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось очистить историю: {str(e)}")
