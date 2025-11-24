import os
import base64
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QFileDialog, QFrame, QProgressBar, QTextEdit,
                               QGroupBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QFont
from Gui.model_handler import model_handler


class ProcessingThread(QThread):
    finished = Signal(object, object, object)
    error = Signal(str)

    def __init__(self, img1_path, img2_path):
        super().__init__()
        self.img1_path = img1_path
        self.img2_path = img2_path

    def run(self):
        try:
            result, confidence, result_image = model_handler.verify_signature(
                self.img1_path, self.img2_path, show_result=True
            )
            self.finished.emit(result, confidence, result_image)
        except Exception as e:
            self.error.emit(str(e))


class ProcessingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.current_image1 = None
        self.current_image2 = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title = QLabel("🔍 Анализ и верификация подписей")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #ffffff; margin: 10px;")
        layout.addWidget(title)

        # Группа загрузки изображений
        upload_group = QGroupBox("Загрузка изображений")
        upload_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        upload_layout = QHBoxLayout(upload_group)

        # Левая панель - эталонная подпись
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        self.btn_load_ref = QPushButton("📁 Загрузить эталонную подпись")
        self.btn_load_ref.setFixedHeight(40)
        self.btn_load_ref.clicked.connect(lambda: self.load_image(1))
        left_panel.addWidget(self.btn_load_ref)

        self.lbl_ref_image = QLabel()
        self.lbl_ref_image.setAlignment(Qt.AlignCenter)
        self.lbl_ref_image.setMinimumSize(350, 250)
        self.lbl_ref_image.setStyleSheet("""
            QLabel {
                border: 3px dashed #555555;
                border-radius: 10px;
                background-color: #1e1e1e;
                color: #cccccc;
                font-size: 14px;
                padding: 20px;
            }
        """)
        self.lbl_ref_image.setText("Эталонная подпись\nне загружена")
        left_panel.addWidget(self.lbl_ref_image)

        self.lbl_ref_name = QLabel("Файл не выбран")
        self.lbl_ref_name.setAlignment(Qt.AlignCenter)
        self.lbl_ref_name.setStyleSheet("color: #cccccc; font-size: 12px; padding: 5px;")
        left_panel.addWidget(self.lbl_ref_name)

        # Правая панель - проверяемая подпись
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)

        self.btn_load_test = QPushButton("📁 Загрузить проверяемую подпись")
        self.btn_load_test.setFixedHeight(40)
        self.btn_load_test.clicked.connect(lambda: self.load_image(2))
        right_panel.addWidget(self.btn_load_test)

        self.lbl_test_image = QLabel()
        self.lbl_test_image.setAlignment(Qt.AlignCenter)
        self.lbl_test_image.setMinimumSize(350, 250)
        self.lbl_test_image.setStyleSheet("""
            QLabel {
                border: 3px dashed #555555;
                border-radius: 10px;
                background-color: #1e1e1e;
                color: #cccccc;
                font-size: 14px;
                padding: 20px;
            }
        """)
        self.lbl_test_image.setText("Проверяемая подпись\nне загружена")
        right_panel.addWidget(self.lbl_test_image)

        self.lbl_test_name = QLabel("Файл не выбран")
        self.lbl_test_name.setAlignment(Qt.AlignCenter)
        self.lbl_test_name.setStyleSheet("color: #cccccc; font-size: 12px; padding: 5px;")
        right_panel.addWidget(self.lbl_test_name)

        upload_layout.addLayout(left_panel)
        upload_layout.addLayout(right_panel)
        layout.addWidget(upload_group)

        # Кнопка анализа
        self.btn_analyze = QPushButton("🚀 Начать анализ подписей")
        self.btn_analyze.setFont(QFont("Arial", 14, QFont.Bold))
        self.btn_analyze.setFixedHeight(50)
        self.btn_analyze.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #34495e;
                color: #7f8c8d;
            }
        """)
        self.btn_analyze.clicked.connect(self.analyze_signatures)
        self.btn_analyze.setEnabled(False)  # Изначально отключена
        layout.addWidget(self.btn_analyze)

        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 5px;
                background-color: #1e1e1e;
                text-align: center;
                color: white;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Группа результатов
        self.result_group = QGroupBox("Результаты анализа")
        self.result_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        self.result_layout = QVBoxLayout(self.result_group)

        # Место для изображения с результатами
        self.lbl_result_image = QLabel()
        self.lbl_result_image.setAlignment(Qt.AlignCenter)
        self.lbl_result_image.setMinimumHeight(400)
        self.lbl_result_image.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border: 2px solid #555555;
                border-radius: 10px;
                color: #cccccc;
            }
        """)
        self.lbl_result_image.setText("Результаты анализа появятся здесь")
        self.result_layout.addWidget(self.lbl_result_image)

        # Детальные результаты
        self.detailed_results = QTextEdit()
        self.detailed_results.setReadOnly(True)
        self.detailed_results.setMaximumHeight(200)
        self.detailed_results.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 2px solid #555555;
                border-radius: 10px;
                color: #ffffff;
                font-size: 13px;
                padding: 10px;
            }
        """)
        self.result_layout.addWidget(self.detailed_results)

        layout.addWidget(self.result_group)
        self.result_group.setVisible(False)

    def load_image(self, image_type):
        """Загрузка изображения с правильной проверкой типа"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение подписи",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)"
        )

        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Масштабирование изображения для preview
                scaled_pixmap = pixmap.scaled(350, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                if image_type == 1:
                    self.current_image1 = file_path
                    self.lbl_ref_image.setPixmap(scaled_pixmap)
                    self.lbl_ref_name.setText(os.path.basename(file_path))
                    self.lbl_ref_name.setStyleSheet("color: #27ae60; font-size: 12px; padding: 5px;")
                else:
                    self.current_image2 = file_path
                    self.lbl_test_image.setPixmap(scaled_pixmap)
                    self.lbl_test_name.setText(os.path.basename(file_path))
                    self.lbl_test_name.setStyleSheet("color: #27ae60; font-size: 12px; padding: 5px;")

                # Правильная проверка для активации кнопки анализа
                self.update_analyze_button_state()

    def update_analyze_button_state(self):
        """Обновление состояния кнопки анализа на основе загруженных изображений"""
        # Проверяем, что оба изображения загружены (не None и не пустые строки)
        both_loaded = (self.current_image1 is not None and
                       self.current_image2 is not None and
                       len(str(self.current_image1).strip()) > 0 and
                       len(str(self.current_image2).strip()) > 0)

        self.btn_analyze.setEnabled(bool(both_loaded))

    def analyze_signatures(self):
        """Запуск анализа подписей"""
        # Дополнительная проверка перед анализом
        if not self.current_image1 or not self.current_image2:
            self.show_error_message("Пожалуйста, загрузите обе подписи для анализа")
            return

        # Проверяем существование файлов
        if not os.path.exists(self.current_image1) or not os.path.exists(self.current_image2):
            self.show_error_message("Один или оба файла изображений не найдены")
            return

        self.btn_analyze.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # indeterminate progress
        self.result_group.setVisible(False)

        # Запуск анализа в отдельном потоке
        self.thread = ProcessingThread(self.current_image1, self.current_image2)
        self.thread.finished.connect(self.on_analysis_finished)
        self.thread.error.connect(self.on_analysis_error)
        self.thread.start()

    def show_error_message(self, message):
        """Показать сообщение об ошибке"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Ошибка", message)

    def on_analysis_finished(self, result, confidence, result_image):
        """Обработка завершения анализа"""
        self.progress_bar.setVisible(False)
        self.btn_analyze.setEnabled(True)
        self.result_group.setVisible(True)

        # Отображение результата
        if result_image:
            try:
                pixmap = QPixmap()
                pixmap.loadFromData(base64.b64decode(result_image))
                scaled_pixmap = pixmap.scaled(800, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lbl_result_image.setPixmap(scaled_pixmap)
            except Exception as e:
                print(f"Ошибка при загрузке изображения результата: {e}")
                self.lbl_result_image.setText("Ошибка отображения результата")

        # Детальные результаты
        analysis = model_handler.get_detailed_analysis(confidence, result)
        self.display_detailed_results(analysis)

        # Добавляем в историю
        if hasattr(self.main_window, 'history_tab'):
            history_text = f"Анализ подписей: {analysis['percentage']} уверенности - {analysis['verdict']}"
            self.main_window.history_tab.add_to_history(
                f"{os.path.basename(self.current_image1)} vs {os.path.basename(self.current_image2)}",
                f"Результат: {analysis['verdict']}\nУверенность: {analysis['percentage']}\nУровень: {analysis['confidence_text']}",
                "Анализ подписи"
            )

    def on_analysis_error(self, error_msg):
        """Обработка ошибки анализа"""
        self.progress_bar.setVisible(False)
        self.btn_analyze.setEnabled(True)
        self.detailed_results.setHtml(f"""
        <div style='color: #e74c3c; text-align: center; padding: 20px;'>
            <h2 style='margin: 10px;'>❌ Ошибка анализа</h2>
            <p style='font-size: 14px;'>{error_msg}</p>
        </div>
        """)

    def display_detailed_results(self, analysis):
        """Отображение детальных результатов с красивым форматированием"""

        # Определяем CSS классы для уверенности
        confidence_color = {
            'high': '#27ae60',
            'medium': '#f39c12',
            'low': '#e74c3c'
        }.get(analysis['confidence_level'], '#cccccc')

        # Создаем красивый HTML вывод
        html = f"""
        <div style="text-align: center; padding: 20px;">
            <!-- Основной вердикт -->
            <div style="margin: 15px 0;">
                <h1 style="color: {analysis['color']}; margin: 10px; font-size: 28px;">
                    {analysis['icon']} {analysis['verdict']}
                </h1>
            </div>

            <!-- Уровень уверенности -->
            <div style="background-color: #2c3e50; border-radius: 10px; padding: 15px; margin: 15px 0;">
                <div style="font-size: 48px; color: {confidence_color}; font-weight: bold; margin: 10px;">
                    {analysis['percentage']}
                </div>
                <div style="color: #ecf0f1; font-size: 16px; margin: 5px;">
                    {analysis['confidence_icon']} {analysis['confidence_text']}
                </div>
            </div>

            <!-- Разделитель -->
            <hr style="border: 1px solid #34495e; margin: 20px 0;">

            <!-- Информация о файлах -->
            <div style="display: flex; justify-content: space-around; margin: 20px 0;">
                <div style="text-align: center;">
                    <div style="color: #3498db; font-weight: bold;">📄 ЭТАЛОН</div>
                    <div style="color: #bdc3c7; font-size: 12px;">{os.path.basename(self.current_image1) if self.current_image1 else 'Не загружено'}</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: #e67e22; font-weight: bold;">🔍 ПРОВЕРЯЕМАЯ</div>
                    <div style="color: #bdc3c7; font-size: 12px;">{os.path.basename(self.current_image2) if self.current_image2 else 'Не загружено'}</div>
                </div>
            </div>

            <!-- Дополнительная информация -->
            <div style="background-color: #34495e; border-radius: 8px; padding: 10px; margin: 15px 0;">
                <div style="color: #ecf0f1; font-size: 12px;">
                    Модель: SiameseViT • Время анализа: < 2 сек • Разрешение: 128x256
                </div>
            </div>
        </div>
        """

        self.detailed_results.setHtml(html)

    def load_image_from_menu(self, file_path):
        """Загрузка изображения из главного меню (для совместимости)"""
        if not self.current_image1:
            self.current_image1 = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(350, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lbl_ref_image.setPixmap(scaled_pixmap)
                self.lbl_ref_name.setText(os.path.basename(file_path))
                self.lbl_ref_name.setStyleSheet("color: #27ae60; font-size: 12px; padding: 5px;")
        elif not self.current_image2:
            self.current_image2 = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(350, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lbl_test_image.setPixmap(scaled_pixmap)
                self.lbl_test_name.setText(os.path.basename(file_path))
                self.lbl_test_name.setStyleSheet("color: #27ae60; font-size: 12px; padding: 5px;")
        else:
            # Если оба уже загружены, заменяем проверяемую
            self.current_image2 = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(350, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lbl_test_image.setPixmap(scaled_pixmap)
                self.lbl_test_name.setText(os.path.basename(file_path))
                self.lbl_test_name.setStyleSheet("color: #27ae60; font-size: 12px; padding: 5px;")

        self.update_analyze_button_state()