from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGroupBox, QFileDialog, QProgressBar,
                               QMessageBox, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
import os
import sys
from PIL import Image
import torch
import torchvision.transforms as transforms

from Grafic.models.scanner import SignatureScanner


class ScannerWidget(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.scanner = SignatureScanner(config)
        self.original_image_path = None
        self.test_image_path = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Заголовок
        title = QLabel("Проверка подписей")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Панель выбора изображений
        images_layout = QHBoxLayout()

        # Оригинальная подпись
        self.original_group = self.create_image_group("Оригинальная подпись", "original")
        images_layout.addWidget(self.original_group)

        # Проверяемая подпись  
        self.test_group = self.create_image_group("Проверяемая подпись", "test")
        images_layout.addWidget(self.test_group)

        layout.addLayout(images_layout)

        # Кнопка проверки
        self.scan_btn = QPushButton("🔍 Запустить проверку")
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                margin: 20px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.scan_btn.clicked.connect(self.run_scan)
        self.scan_btn.setEnabled(False)
        layout.addWidget(self.scan_btn)

        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Результат
        self.result_group = self.create_result_group()
        layout.addWidget(self.result_group)

        layout.addStretch()

    def create_image_group(self, title, image_type):
        """Создание группы для отображения изображения"""
        group = QGroupBox(title)
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Метка для изображения
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("""
            border: 2px dashed #ccc;
            border-radius: 10px;
            background-color: #f8f9fa;
            min-height: 300px;
        """)
        image_label.setText("Изображение не выбрано")
        layout.addWidget(image_label)

        # Кнопка выбора
        select_btn = QPushButton("📁 Выбрать изображение")
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)

        if image_type == "original":
            select_btn.clicked.connect(lambda: self.select_image("original"))
            self.original_image_label = image_label
        else:
            select_btn.clicked.connect(lambda: self.select_image("test"))
            self.test_image_label = image_label

        layout.addWidget(select_btn)

        return group

    def create_result_group(self):
        """Создание группы для отображения результата"""
        group = QGroupBox("Результат проверки")
        layout = QVBoxLayout()
        group.setLayout(layout)

        self.result_label = QLabel("Результат появится здесь после проверки")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("""
            font-size: 18px;
            padding: 30px;
            background-color: #f8f9fa;
            border-radius: 10px;
        """)
        layout.addWidget(self.result_label)

        self.confidence_label = QLabel("")
        self.confidence_label.setAlignment(Qt.AlignCenter)
        self.confidence_label.setStyleSheet("font-size: 16px; margin: 10px;")
        layout.addWidget(self.confidence_label)

        return group

    def select_image(self, image_type):
        """Выбор изображения"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Выберите {image_type} изображение",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            # Загрузка и отображение изображения
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Масштабируем изображение для preview
                scaled_pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                if image_type == "original":
                    self.original_image_label.setPixmap(scaled_pixmap)
                    self.original_image_path = file_path
                else:
                    self.test_image_label.setPixmap(scaled_pixmap)
                    self.test_image_path = file_path

                # Активируем кнопку проверки если оба изображения выбраны
                self.update_scan_button()

    def update_scan_button(self):
        """Активация кнопки проверки при выборе обоих изображений"""
        if self.original_image_path and self.test_image_path:
            self.scan_btn.setEnabled(True)
        else:
            self.scan_btn.setEnabled(False)

    def run_scan(self):
        """Запуск проверки подписей"""
        if not self.original_image_path or not self.test_image_path:
            QMessageBox.warning(self, "Ошибка", "Выберите оба изображения!")
            return

        try:
            self.progress_bar.setVisible(True)
            self.scan_btn.setEnabled(False)

            # Запуск проверки
            result, confidence = self.scanner.verify_signatures(
                self.original_image_path,
                self.test_image_path
            )

            # Отображение результата
            self.display_result(result, confidence)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при проверке: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
            self.scan_btn.setEnabled(True)

    def display_result(self, result, confidence):
        """Отображение результата проверки"""
        if result:
            result_text = "✅ ПОДПИСЬ ОРИГИНАЛЬНА"
            color = "green"
            status = "оригинальная"
        else:
            result_text = "❌ ПОДПИСЬ ПОДДЕЛЬНА"
            color = "red"
            status = "поддельная"

        self.result_label.setText(f"""
        <div style='font-size: 24px; font-weight: bold; color: {color};'>
            {result_text}
        </div>
        """)

        self.confidence_label.setText(f"""
        <div style='font-size: 18px;'>
            Уверенность: <b>{confidence * 100:.2f}%</b><br>
            Статус: <b>{status}</b>
        </div>
        """)

        # Сохранение в историю
        self.scanner.save_to_history(
            self.original_image_path,
            self.test_image_path,
            result,
            confidence
        )
