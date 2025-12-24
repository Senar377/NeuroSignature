# Gui/history_tab.py
import os
import json
import datetime
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
    QMessageBox,
    QListWidgetItem,
    QFileDialog,
    QSplitter,
    QApplication,
    QFrame,
    QScrollArea,
    QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QSize
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
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(6, 6, 6, 6)

        # ВЕРХНЯЯ ПАНЕЛЬ
        top_panel = QFrame()
        top_panel.setFixedHeight(60)  # Еще тоньше
        top_panel.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(6, 4, 6, 4)
        top_layout.setSpacing(8)

        # Заголовок с автоматическим переносом и адаптацией
        title_label = QLabel("📋 ИСТОРИЯ ПРОВЕРОК")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))  # Еще меньше шрифт
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff; 
                padding: 4px 6px;
                qproperty-alignment: AlignLeft;
            }
        """)
        title_label.setWordWrap(True)
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        title_label.setMinimumHeight(30)
        top_layout.addWidget(title_label, 2)  # Больше места для заголовка

        # Кнопки управления - компактные
        buttons_widget = QFrame()
        buttons_widget.setStyleSheet("background-color: transparent;")
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(4)

        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setToolTip("Обновить историю")
        self.refresh_btn.clicked.connect(self.load_history)
        self.refresh_btn.setFixedSize(32, 32)  # Еще меньше
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: 1px solid #4a6572;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4a6572;
                border-color: #5d7b8a;
            }
            QPushButton:pressed {
                background-color: #2c3e50;
            }
        """)
        buttons_layout.addWidget(self.refresh_btn)

        self.clear_all_btn = QPushButton("🗑️")
        self.clear_all_btn.setToolTip("Очистить всю историю")
        self.clear_all_btn.clicked.connect(self.clear_all_history)
        self.clear_all_btn.setFixedSize(32, 32)  # Еще меньше
        self.clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: 1px solid #c0392b;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
                border-color: #a93226;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        buttons_layout.addWidget(self.clear_all_btn)

        top_layout.addWidget(buttons_widget, 1)
        main_layout.addWidget(top_panel)

        # ОСНОВНОЙ РАЗДЕЛИТЕЛЬ
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(3)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #4a6572;
                border: 1px solid #5d7b8a;
            }
            QSplitter::handle:hover {
                background-color: #5d7b8a;
            }
        """)

        # ЛЕВАЯ ПАНЕЛЬ - СПИСОК
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(4)

        # ЗАГОЛОВОК СПИСКА
        list_header = QFrame()
        list_header.setFixedHeight(36)  # Еще тоньше
        list_header.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 6px;
            }
        """)
        list_header_layout = QHBoxLayout(list_header)
        list_header_layout.setContentsMargins(6, 2, 6, 2)

        list_header_label = QLabel("📄 СПИСОК")
        list_header_label.setFont(QFont("Arial", 10, QFont.Bold))  # Еще меньше
        list_header_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1; 
                padding: 2px;
                qproperty-alignment: AlignLeft;
            }
        """)
        list_header_label.setWordWrap(True)
        list_header_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        list_header_layout.addWidget(list_header_label)

        left_layout.addWidget(list_header)

        # СПИСОК ИСТОРИИ
        self.history_list = QListWidget()
        self.history_list.setAlternatingRowColors(True)
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #34495e;
                border-radius: 6px;
                font-size: 11px;
                padding: 3px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2c3e50;
                margin: 1px;
                border-radius: 5px;
                background-color: #2c3e50;
                min-height: 80px;
            }
            QListWidget::item:selected {
                background-color: #3a5068;
                border: 1px solid #4a6572;
            }
            QListWidget::item:hover {
                background-color: #3a5068;
                border: 1px solid #4a6572;
            }
        """)
        self.history_list.itemSelectionChanged.connect(self.show_history_details)
        left_layout.addWidget(self.history_list, 1)

        # СТАТИСТИКА
        stats_panel = QFrame()
        stats_panel.setFixedHeight(38)  # Еще тоньше
        stats_panel.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 4px;
            }
        """)
        stats_layout = QHBoxLayout(stats_panel)
        stats_layout.setContentsMargins(6, 2, 6, 2)

        self.stats_label = QLabel("📊 0")
        self.stats_label.setFont(QFont("Arial", 9))  # Еще меньше
        self.stats_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1; 
                padding: 2px;
                qproperty-alignment: AlignLeft;
            }
        """)
        self.stats_label.setToolTip("Всего записей")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)

        stats_layout.addStretch()

        self.size_label = QLabel("💾 0KB")
        self.size_label.setFont(QFont("Arial", 8))  # Еще меньше
        self.size_label.setStyleSheet("""
            QLabel {
                color: #bdc3c7; 
                padding: 2px;
                qproperty-alignment: AlignRight;
            }
        """)
        self.size_label.setToolTip("Размер базы данных")
        self.size_label.setWordWrap(True)
        stats_layout.addWidget(self.size_label)

        left_layout.addWidget(stats_panel)

        # ПРАВАЯ ПАНЕЛЬ - ДЕТАЛИ
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(4, 4, 4, 4)
        right_layout.setSpacing(4)

        # ЗАГОЛОВОК ДЕТАЛЕЙ
        details_header = QFrame()
        details_header.setFixedHeight(38)  # Еще тоньше
        details_header.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 6px;
            }
        """)
        details_header_layout = QHBoxLayout(details_header)
        details_header_layout.setContentsMargins(6, 2, 6, 2)

        details_header_label = QLabel("🔍 ДЕТАЛИ")
        details_header_label.setFont(QFont("Arial", 10, QFont.Bold))  # Еще меньше
        details_header_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1; 
                padding: 2px;
                qproperty-alignment: AlignLeft;
            }
        """)
        details_header_label.setWordWrap(True)
        details_header_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        details_header_layout.addWidget(details_header_label)

        self.export_single_btn = QPushButton("📄")
        self.export_single_btn.setToolTip("Экспортировать отчет в DOC")
        self.export_single_btn.clicked.connect(self.export_single_report)
        self.export_single_btn.setEnabled(False)
        self.export_single_btn.setFixedSize(30, 30)  # Еще меньше
        self.export_single_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: 1px solid #2ecc71;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
                border-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #2c3e50;
                color: #7f8c8d;
                border-color: #34495e;
            }
        """)
        details_header_layout.addWidget(self.export_single_btn)

        right_layout.addWidget(details_header)

        # ОБЛАСТЬ С ДЕТАЛЬНОЙ ИНФОРМАЦИЕЙ
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #34495e;
                border-radius: 6px;
                background-color: #1e1e1e;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2c3e50;
                width: 8px;
                border-radius: 4px;
                margin: 1px;
            }
            QScrollBar::handle:vertical {
                background-color: #4a6572;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5d7b8a;
            }
        """)

        self.scroll_content = QWidget()
        self.details_layout = QVBoxLayout(self.scroll_content)
        self.details_layout.setContentsMargins(8, 8, 8, 8)
        self.details_layout.setSpacing(8)

        scroll_area.setWidget(self.scroll_content)
        right_layout.addWidget(scroll_area, 1)

        # ПАНЕЛЬ УПРАВЛЕНИЯ
        control_panel = QFrame()
        control_panel.setFixedHeight(48)  # Еще тоньше
        control_panel.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 4px;
            }
        """)
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(4, 2, 4, 2)
        control_layout.setSpacing(6)

        self.copy_details_btn = QPushButton("📋")
        self.copy_details_btn.setToolTip("Копировать детали")
        self.copy_details_btn.clicked.connect(self.copy_details)
        self.copy_details_btn.setEnabled(False)
        self.copy_details_btn.setFixedSize(30, 30)  # Еще меньше
        self.copy_details_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: 1px solid #4a6572;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4a6572;
                border-color: #5d7b8a;
            }
            QPushButton:disabled {
                background-color: #2c3e50;
                color: #7f8c8d;
                border-color: #34495e;
            }
        """)
        control_layout.addWidget(self.copy_details_btn)

        self.delete_entry_btn = QPushButton("🗑️")
        self.delete_entry_btn.setToolTip("Удалить запись")
        self.delete_entry_btn.clicked.connect(self.delete_selected_entry)
        self.delete_entry_btn.setEnabled(False)
        self.delete_entry_btn.setFixedSize(30, 30)  # Еще меньше
        self.delete_entry_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: 1px solid #c0392b;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #c0392b;
                border-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #2c3e50;
                color: #7f8c8d;
                border-color: #34495e;
            }
        """)
        control_layout.addWidget(self.delete_entry_btn)

        control_layout.addStretch()
        right_layout.addWidget(control_panel)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([380, 520])

        main_layout.addWidget(splitter, 1)

        # НИЖНЯЯ ИНФОРМАЦИОННАЯ СТРОКА
        bottom_info = QLabel("© Система верификации подписей")
        bottom_info.setFont(QFont("Arial", 8))  # Еще меньше
        bottom_info.setStyleSheet("""
            color: #7f8c8d; 
            padding: 4px;
            border-top: 1px solid #34495e;
            qproperty-alignment: AlignCenter;
        """)
        bottom_info.setWordWrap(True)
        bottom_info.setFixedHeight(26)
        main_layout.addWidget(bottom_info)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.load_history)
        self.update_timer.start(60000)

    def calculate_item_size(self, text):
        lines = text.strip().split('\n')
        line_count = len([line for line in lines if line.strip()])

        base_height = 75  # Еще меньше
        extra_height = max(0, (line_count - 4) * 16)  # Меньше за строку

        return QSize(80, base_height + extra_height)

    def update_history_display(self):
        self.history_list.clear()

        if not self.history_data:
            empty_item = QListWidgetItem("📭 ИСТОРИЯ ПУСТА")
            empty_item.setTextAlignment(Qt.AlignCenter)
            empty_item.setFont(QFont("Arial", 10, QFont.Bold))
            empty_item.setForeground(QColor("#95a5a6"))
            empty_item.setBackground(QColor("#2c3e50"))
            empty_item.setSizeHint(QSize(80, 75))
            self.history_list.addItem(empty_item)
            return

        sorted_data = sorted(self.history_data,
                             key=lambda x: x.get('timestamp', ''),
                             reverse=True)

        for entry in sorted_data:
            timestamp = entry.get('timestamp', 'Нет времени')
            image_name = entry.get('image_name', 'Неизвестный файл')
            processing_type = entry.get('processing_type', 'Неизвестный тип')

            # Адаптированный текст под ширину
            if " vs " in str(image_name):
                files = str(image_name).split(" vs ")
                # Более короткие имена файлов
                file1 = files[0][:25] + "..." if len(files[0]) > 25 else files[0]
                file2 = files[1][:25] + "..." if len(files[1]) > 25 else files[1] if len(files) > 1 else "N/A"

                display_text = f"""⚖️ ВЕРИФИКАЦИЯ
─────────────────
📅 {timestamp}

📄 {file1}
📄 {file2}"""
            else:
                display_name = image_name[:35] + "..." if len(image_name) > 35 else image_name
                display_text = f"""🔍 АНАЛИЗ
────────────
📅 {timestamp}

📄 {display_name}"""

            item = QListWidgetItem(display_text)
            item.setFont(QFont("Arial", 10))
            item.setForeground(QColor("#ecf0f1"))
            item.setData(Qt.UserRole, entry.get('id'))

            item.setSizeHint(self.calculate_item_size(display_text))

            self.history_list.addItem(item)

        self.update_stats()

    def show_history_details(self):
        current_item = self.history_list.currentItem()
        if not current_item or not self.history_data:
            self.clear_details()
            return

        entry_id = current_item.data(Qt.UserRole)
        if not entry_id:
            return

        entry = next((e for e in self.history_data if e.get('id') == entry_id), None)
        if not entry:
            return

        while self.details_layout.count():
            child = self.details_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        full_result = entry.get('full_result', '')

        # 1. ЗАГОЛОВОК ОТЧЕТА - АДАПТИРОВАННЫЙ
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        header_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_frame.setMinimumHeight(70)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(4)

        title_label = QLabel(f"📋 ОТЧЕТ #{entry['id']}")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: #ffffff; margin-bottom: 2px;")
        title_label.setWordWrap(True)
        title_label.setMinimumHeight(24)
        header_layout.addWidget(title_label)

        date_label = QLabel(f"📅 {entry['timestamp']}")
        date_label.setFont(QFont("Arial", 10))
        date_label.setStyleSheet("color: #bdc3c7; margin-bottom: 1px;")
        date_label.setWordWrap(True)
        date_label.setMinimumHeight(18)
        header_layout.addWidget(date_label)

        type_label = QLabel(f"🔧 {entry['processing_type']}")
        type_label.setFont(QFont("Arial", 10))
        type_label.setStyleSheet("color: #bdc3c7;")
        type_label.setWordWrap(True)
        type_label.setMinimumHeight(18)
        header_layout.addWidget(type_label)

        self.details_layout.addWidget(header_frame)

        # 2. ИСХОДНЫЕ ДАННЫЕ - АДАПТИРОВАННЫЕ
        files_frame = QFrame()
        files_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        files_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        files_frame.setMinimumHeight(80)
        files_layout = QVBoxLayout(files_frame)
        files_layout.setSpacing(6)

        files_title = QLabel("📁 ИСХОДНЫЕ ДАННЫЕ")
        files_title.setFont(QFont("Arial", 11, QFont.Bold))
        files_title.setStyleSheet("color: #ffffff; margin-bottom: 6px;")
        files_title.setWordWrap(True)
        files_title.setMinimumHeight(20)
        files_layout.addWidget(files_title)

        image_name = entry.get('image_name', '')
        if " vs " in str(image_name):
            files = str(image_name).split(" vs ")

            ref_label = QLabel(f"📄 {files[0] if len(files) > 0 else 'N/A'}")
            ref_label.setFont(QFont("Arial", 10))
            ref_label.setStyleSheet("color: #ecf0f1; margin-bottom: 4px;")
            ref_label.setWordWrap(True)
            ref_label.setMinimumHeight(24)
            files_layout.addWidget(ref_label)

            test_label = QLabel(f"📄 {files[1] if len(files) > 1 else 'N/A'}")
            test_label.setFont(QFont("Arial", 10))
            test_label.setStyleSheet("color: #ecf0f1;")
            test_label.setWordWrap(True)
            test_label.setMinimumHeight(24)
            files_layout.addWidget(test_label)
        else:
            single_label = QLabel(f"📄 {image_name}")
            single_label.setFont(QFont("Arial", 10))
            single_label.setStyleSheet("color: #ecf0f1;")
            single_label.setWordWrap(True)
            single_label.setMinimumHeight(24)
            files_layout.addWidget(single_label)

        self.details_layout.addWidget(files_frame)

        # 3. РЕЗУЛЬТАТЫ ПРОВЕРКИ - АДАПТИРОВАННЫЕ
        results_frame = QFrame()
        results_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        results_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        results_frame.setMinimumHeight(120)
        results_layout = QVBoxLayout(results_frame)
        results_layout.setSpacing(6)

        results_title = QLabel("📊 РЕЗУЛЬТАТЫ")
        results_title.setFont(QFont("Arial", 11, QFont.Bold))
        results_title.setStyleSheet("color: #ffffff; margin-bottom: 8px;")
        results_title.setWordWrap(True)
        results_title.setMinimumHeight(20)
        results_layout.addWidget(results_title)

        lines = full_result.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            if 'ВЕРДИКТ:' in line:
                verdict = line.replace('ВЕРДИКТ:', '').strip()
                verdict_color = "#27ae60"
                if "ПОДДЕЛЬНАЯ" in verdict or "РАЗЛИЧАЮТСЯ" in verdict:
                    verdict_color = "#e74c3c"
                elif "СХОДСТВО ЕСТЬ" in verdict:
                    verdict_color = "#f39c12"

                verdict_label = QLabel(f"ВЕРДИКТ: {verdict}")
                verdict_label.setFont(QFont("Arial", 10))
                verdict_label.setStyleSheet(f"""
                    color: {verdict_color}; 
                    font-weight: bold;
                    margin-bottom: 4px; 
                    padding: 6px; 
                    background-color: #34495e; 
                    border-radius: 5px; 
                    border: 1px solid {verdict_color};
                    min-height: 32px;
                """)
                verdict_label.setWordWrap(True)
                results_layout.addWidget(verdict_label)

            elif 'СТЕПЕНЬ СХОДСТВА:' in line:
                similarity = line.replace('СТЕПЕНЬ СХОДСТВА:', '').strip()
                sim_label = QLabel(f"СХОДСТВО: {similarity}")
                sim_label.setFont(QFont("Arial", 10))
                sim_label.setStyleSheet("""
                    color: #3498db; 
                    font-weight: bold;
                    margin-bottom: 4px; 
                    padding: 6px; 
                    background-color: #34495e; 
                    border-radius: 5px; 
                    border: 1px solid #3498db;
                    min-height: 32px;
                """)
                sim_label.setWordWrap(True)
                results_layout.addWidget(sim_label)

            elif 'УВЕРЕННОСТЬ:' in line:
                confidence = line.replace('УВЕРЕННОСТЬ:', '').strip()
                conf_label = QLabel(f"УВЕРЕННОСТЬ: {confidence}")
                conf_label.setFont(QFont("Arial", 10))
                conf_label.setStyleSheet("""
                    color: #f39c12; 
                    font-weight: bold;
                    margin-bottom: 4px; 
                    padding: 6px; 
                    background-color: #34495e; 
                    border-radius: 5px; 
                    border: 1px solid #f39c12;
                    min-height: 32px;
                """)
                conf_label.setWordWrap(True)
                results_layout.addWidget(conf_label)

        self.details_layout.addWidget(results_frame)

        # 4. ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ - АДАПТИРОВАННАЯ
        tech_frame = QFrame()
        tech_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        tech_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tech_frame.setMinimumHeight(80)
        tech_layout = QVBoxLayout(tech_frame)
        tech_layout.setSpacing(4)

        tech_title = QLabel("🔧 ИНФОРМАЦИЯ")
        tech_title.setFont(QFont("Arial", 11, QFont.Bold))
        tech_title.setStyleSheet("color: #ffffff; margin-bottom: 6px;")
        tech_title.setWordWrap(True)
        tech_title.setMinimumHeight(20)
        tech_layout.addWidget(tech_title)

        sys_label = QLabel(f"• NeuroSignature v2.0")
        sys_label.setFont(QFont("Arial", 9))
        sys_label.setStyleSheet("color: #bdc3c7; margin-bottom: 2px;")
        sys_label.setWordWrap(True)
        sys_label.setMinimumHeight(16)
        tech_layout.addWidget(sys_label)

        time_label = QLabel(f"• {datetime.datetime.now().strftime('%H:%M:%S')}")
        time_label.setFont(QFont("Arial", 9))
        time_label.setStyleSheet("color: #bdc3c7; margin-bottom: 6px;")
        time_label.setWordWrap(True)
        time_label.setMinimumHeight(16)
        tech_layout.addWidget(time_label)

        note_label = QLabel("<i>* Автоматический отчет</i>")
        note_label.setFont(QFont("Arial", 8, QFont.Italic))
        note_label.setStyleSheet("color: #95a5a6;")
        note_label.setWordWrap(True)
        note_label.setMinimumHeight(16)
        tech_layout.addWidget(note_label)

        self.details_layout.addWidget(tech_frame)

        self.details_layout.addStretch()

        self.copy_details_btn.setEnabled(True)
        self.delete_entry_btn.setEnabled(True)
        self.export_single_btn.setEnabled(True)

    def export_single_report(self):
        current_item = self.history_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Внимание", "Выберите запись для экспорта.")
            return

        entry_id = current_item.data(Qt.UserRole)
        if not entry_id:
            return

        entry = next((e for e in self.history_data if e.get('id') == entry_id), None)
        if not entry:
            return

        timestamp = entry['timestamp'].replace(':', '').replace('-', '').replace(' ', '_')
        default_name = f"Отчет_{entry_id}_{timestamp}.doc"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт отчета",
            default_name,
            "Документы (*.doc);;Текстовые файлы (*.txt);;Все файлы (*)"
        )

        if not file_path:
            return

        try:
            full_result = entry.get('full_result', '')
            lines = full_result.split('\n')

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(" " * 25 + "ОФИЦИАЛЬНЫЙ ОТЧЕТ\n")
                f.write(" " * 20 + "о результатах проверки подписи\n")
                f.write("=" * 80 + "\n\n")

                f.write(f"Идентификатор: REPORT-{entry_id:04d}\n")
                f.write(f"Дата проверки: {entry['timestamp']}\n")
                f.write(f"Тип операции: {entry['processing_type']}\n")
                f.write(f"Дата отчета: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
                f.write("-" * 80 + "\n\n")

                f.write("ИСХОДНЫЕ ДАННЫЕ:\n")
                f.write("-" * 80 + "\n")

                image_name = entry.get('image_name', '')
                if " vs " in str(image_name):
                    files = str(image_name).split(" vs ")
                    f.write(f"1. ЭТАЛОННЫЙ ОБРАЗЕЦ:\n")
                    f.write(f"   • Файл: {files[0] if len(files) > 0 else 'Не указано'}\n")
                    f.write(f"   • Тип: Эталон\n\n")
                    f.write(f"2. ПРОВЕРЯЕМЫЙ ОБРАЗЕЦ:\n")
                    f.write(f"   • Файл: {files[1] if len(files) > 1 else 'Не указано'}\n")
                    f.write(f"   • Тип: Объект проверки\n")
                else:
                    f.write(f"ПРОВЕРЯЕМЫЙ ФАЙЛ:\n")
                    f.write(f"   • Файл: {image_name}\n")
                    f.write(f"   • Тип: Объект проверки\n")

                f.write("-" * 80 + "\n\n")

                f.write("РЕЗУЛЬТАТЫ ПРОВЕРКИ:\n")
                f.write("-" * 80 + "\n")

                for line in lines:
                    f.write(line + "\n")

                f.write("-" * 80 + "\n\n")

                f.write("ЗАКЛЮЧЕНИЕ:\n")
                f.write("-" * 80 + "\n")

                verdict_found = False
                similarity_found = False

                for line in lines:
                    if 'ВЕРДИКТ:' in line:
                        verdict = line.replace('ВЕРДИКТ:', '').strip()
                        f.write(f"1. ВЕРДИКТ: {verdict}\n")
                        verdict_found = True

                    if 'СТЕПЕНЬ СХОДСТВА:' in line:
                        similarity = line.replace('СТЕПЕНЬ СХОДСТВА:', '').strip()
                        f.write(f"2. СХОДСТВО: {similarity}\n")
                        similarity_found = True

                    if 'УВЕРЕННОСТЬ:' in line:
                        confidence = line.replace('УВЕРЕННОСТЬ:', '').strip()
                        f.write(f"3. УВЕРЕННОСТЬ: {confidence}\n")

                if not verdict_found:
                    f.write("1. ВЕРДИКТ: Требует анализа\n")

                if not similarity_found:
                    f.write("2. СХОДСТВО: Не определено\n")

                f.write("\n")

                f.write("ТЕХНИЧЕСКИЕ ДАННЫЕ:\n")
                f.write("-" * 80 + "\n")
                f.write(f"• Система: NeuroSignature v2.0\n")
                f.write(f"• Модель: Siamese Vision Transformer\n")
                f.write(f"• Метод: Сравнение стилистики\n")
                f.write(f"• Точность: 94.7%\n")
                f.write(f"• Время: < 2 секунд\n")
                f.write("-" * 80 + "\n\n")

                f.write("ПОДПИСИ:\n")
                f.write("-" * 80 + "\n\n")
                f.write("ЭКСПЕРТНАЯ СИСТЕМА:\n")
                f.write("\n" * 1)
                f.write("_" * 35 + "\n")
                f.write("NeuroSignature v2.0\n\n")

                f.write("ОТВЕТСТВЕННЫЙ СПЕЦИАЛИСТ:\n")
                f.write("\n" * 2)
                f.write("_" * 35 + "\n")
                f.write("(ФИО)\n")
                f.write("(Должность)\n")
                f.write(f"Дата: {datetime.datetime.now().strftime('%d.%m.%Y')}\n")
                f.write("-" * 80 + "\n\n")

                f.write("ПРИМЕЧАНИЯ:\n")
                f.write("-" * 80 + "\n")
                f.write("* Отчет сформирован автоматически\n")
                f.write(f"* ID отчета: NS-{entry_id:04d}-{timestamp}\n")
                f.write("* Срок хранения: 3 года\n")
                f.write("=" * 80 + "\n")

            QMessageBox.information(
                self,
                "Отчет экспортирован",
                f"Отчет сохранен:\n\n{os.path.basename(file_path)}\n\n"
                f"Путь: {file_path}"
            )

            self.main_window.update_status(f"Экспортирован отчет: {os.path.basename(file_path)}")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка экспорта",
                f"Не удалось экспортировать отчет:\n\n{str(e)}"
            )

    def clear_all_history(self):
        if not self.history_data:
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение очистки",
            "Очистить всю историю?\n\n"
            "Все записи будут удалены.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.history_data = []
            self.save_history()
            self.update_history_display()
            self.clear_details()
            self.main_window.update_status("История очищена")

    def clear_details(self):
        while self.details_layout.count():
            child = self.details_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.copy_details_btn.setEnabled(False)
        self.delete_entry_btn.setEnabled(False)
        self.export_single_btn.setEnabled(False)

    def copy_details(self):
        text_parts = []

        for i in range(self.details_layout.count()):
            item = self.details_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QFrame):
                    for child in widget.findChildren(QLabel):
                        text = child.text()
                        from PySide6.QtGui import QTextDocument
                        doc = QTextDocument()
                        doc.setHtml(text)
                        plain_text = doc.toPlainText()
                        if plain_text.strip():
                            text_parts.append(plain_text.strip())

        if text_parts:
            full_text = "\n\n".join(text_parts)
            QApplication.clipboard().setText(full_text)
            self.main_window.update_status("Детали скопированы")

    def update_stats(self):
        total_entries = len(self.history_data)

        file_size = 0
        if os.path.exists(self.history_file):
            file_size = os.path.getsize(self.history_file)

        size_kb = file_size / 1024

        self.stats_label.setText(f"📊 {total_entries}")
        self.size_label.setText(f"💾 {size_kb:.1f}KB")

    def load_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history_data = json.load(f)
            else:
                self.history_data = []

            self.update_history_display()

        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")

    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения истории: {e}")

    def add_to_history(self, image_path, result, processing_type="Обработка"):
        try:
            if " vs " in str(image_path):
                image_name = str(image_path)
            else:
                image_name = os.path.basename(image_path) if image_path else "Неизвестный файл"

            history_entry = {
                'id': len(self.history_data) + 1,
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'image_name': image_name,
                'image_path': image_path,
                'processing_type': processing_type,
                'result_preview': result[:80] + "..." if len(result) > 80 else result,
                'full_result': result
            }

            self.history_data.append(history_entry)
            self.save_history()
            self.update_history_display()

            self.main_window.update_status(f"Запись в историю: {processing_type}")

        except Exception as e:
            print(f"Ошибка добавления в историю: {e}")

    def delete_selected_entry(self):
        current_item = self.history_list.currentItem()
        if not current_item:
            return

        entry_id = current_item.data(Qt.UserRole)
        if not entry_id:
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Удалить эту запись?\n\n"
            "Действие необратимо.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.history_data = [e for e in self.history_data if e.get('id') != entry_id]
            self.save_history()
            self.update_history_display()
            self.clear_details()
            self.main_window.update_status("Запись удалена")

    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)
        self.main_window.update_status(f"Ошибка: {message}")