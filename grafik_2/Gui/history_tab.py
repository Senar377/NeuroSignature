# Gui/history_tab.py
import os
import json
import datetime
import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QPushButton, QLabel, QMessageBox, QListWidgetItem,
    QFileDialog, QSplitter, QApplication, QFrame,
    QScrollArea, QSizePolicy, QDialog, QTextEdit
)
from PySide6.QtCore import Qt, QTimer, QSize, QEvent
from PySide6.QtGui import QFont, QColor, QTextDocument


class HistoryTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.history_file = "processing_history.json"
        self.history_data = []
        self.current_theme = "light"
        self.secret_click_count = 0
        self.setup_ui()
        self.load_history()
        self.installEventFilter(self)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.create_header_panel(main_layout)
        self.create_splitter(main_layout)
        self.create_status_bar(main_layout)

        self.update_theme("light")

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.load_history)
        self.update_timer.start(60000)

    def create_header_panel(self, parent_layout):
        self.top_panel = QFrame()
        self.top_panel.setObjectName("topPanel")
        self.top_panel.setFixedHeight(60)

        top_layout = QHBoxLayout(self.top_panel)
        top_layout.setContentsMargins(15, 8, 15, 8)
        top_layout.setSpacing(10)

        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)

        icon_label = QLabel("📋")
        icon_label.setFont(QFont("Arial", 20))
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(icon_label)

        text_label = QLabel("ИСТОРИЯ ПРОВЕРОК")
        text_label.setFont(QFont("Arial", 16, QFont.Bold))
        text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_layout.addWidget(text_label)

        title_layout.addStretch()
        top_layout.addWidget(title_widget, 2)

        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(8)

        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setToolTip("Обновить историю")
        self.refresh_btn.clicked.connect(self.load_history)
        self.refresh_btn.setFixedSize(40, 40)
        self.refresh_btn.setFont(QFont("Arial", 16))
        buttons_layout.addWidget(self.refresh_btn)

        self.clear_all_btn = QPushButton("🗑️")
        self.clear_all_btn.setToolTip("Очистить всю историю")
        self.clear_all_btn.clicked.connect(self.clear_all_history)
        self.clear_all_btn.setFixedSize(40, 40)
        self.clear_all_btn.setFont(QFont("Arial", 16))
        buttons_layout.addWidget(self.clear_all_btn)

        top_layout.addWidget(buttons_widget, 1)
        parent_layout.addWidget(self.top_panel)

    def create_splitter(self, parent_layout):
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(4)
        self.splitter.setChildrenCollapsible(False)

        left_widget = self.create_list_panel()
        right_widget = self.create_details_panel()

        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(right_widget)

        self.splitter.setStretchFactor(0, 4)
        self.splitter.setStretchFactor(1, 6)

        parent_layout.addWidget(self.splitter, 1)

    def create_list_panel(self):
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 5, 0)
        left_layout.setSpacing(5)

        self.list_header = QFrame()
        self.list_header.setObjectName("listHeader")
        self.list_header.setFixedHeight(40)

        list_header_layout = QHBoxLayout(self.list_header)
        list_header_layout.setContentsMargins(10, 5, 10, 5)

        list_icon = QLabel("📄")
        list_icon.setFont(QFont("Arial", 14))
        list_header_layout.addWidget(list_icon)

        list_title = QLabel("СПИСОК ЗАПИСЕЙ")
        list_title.setFont(QFont("Arial", 11, QFont.Bold))
        list_header_layout.addWidget(list_title)

        list_header_layout.addStretch()

        self.entries_count = QLabel("0")
        self.entries_count.setFont(QFont("Arial", 10))
        self.entries_count.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        list_header_layout.addWidget(self.entries_count)

        left_layout.addWidget(self.list_header)

        self.history_list = QListWidget()
        self.history_list.setObjectName("historyList")
        self.history_list.setAlternatingRowColors(True)
        self.history_list.setSpacing(2)
        self.history_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.history_list.setHorizontalScrollMode(QListWidget.ScrollPerPixel)
        self.history_list.itemSelectionChanged.connect(self.show_history_details)
        self.history_list.itemDoubleClicked.connect(self.check_history_easter_egg_click)

        self.history_list.setGridSize(QSize(200, 100))
        self.history_list.setIconSize(QSize(32, 32))

        left_layout.addWidget(self.history_list, 1)

        self.create_stats_panel(left_layout)

        return left_widget

    def create_stats_panel(self, parent_layout):
        self.stats_panel = QFrame()
        self.stats_panel.setObjectName("statsPanel")
        self.stats_panel.setFixedHeight(50)

        stats_layout = QHBoxLayout(self.stats_panel)
        stats_layout.setContentsMargins(15, 5, 15, 5)
        stats_layout.setSpacing(15)

        stats_widget1 = QWidget()
        stats_layout1 = QHBoxLayout(stats_widget1)
        stats_layout1.setContentsMargins(0, 0, 0, 0)
        stats_layout1.setSpacing(5)

        stats_icon1 = QLabel("📊")
        stats_icon1.setFont(QFont("Arial", 12))
        stats_layout1.addWidget(stats_icon1)

        self.stats_label = QLabel("0 записей")
        self.stats_label.setFont(QFont("Arial", 10))
        stats_layout1.addWidget(self.stats_label)

        stats_layout.addWidget(stats_widget1)

        stats_widget2 = QWidget()
        stats_layout2 = QHBoxLayout(stats_widget2)
        stats_layout2.setContentsMargins(0, 0, 0, 0)
        stats_layout2.setSpacing(5)

        stats_icon2 = QLabel("💾")
        stats_icon2.setFont(QFont("Arial", 12))
        stats_layout2.addWidget(stats_icon2)

        self.size_label = QLabel("0 KB")
        self.size_label.setFont(QFont("Arial", 10))
        stats_layout2.addWidget(self.size_label)

        stats_layout.addWidget(stats_widget2)

        stats_layout.addStretch()

        parent_layout.addWidget(self.stats_panel)

    def create_details_panel(self):
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 0, 0, 0)
        right_layout.setSpacing(5)

        self.details_header = QFrame()
        self.details_header.setObjectName("detailsHeader")
        self.details_header.setFixedHeight(40)

        details_header_layout = QHBoxLayout(self.details_header)
        details_header_layout.setContentsMargins(10, 5, 10, 5)

        details_icon = QLabel("🔍")
        details_icon.setFont(QFont("Arial", 14))
        details_header_layout.addWidget(details_icon)

        details_title = QLabel("ДЕТАЛЬНАЯ ИНФОРМАЦИЯ")
        details_title.setFont(QFont("Arial", 11, QFont.Bold))
        details_header_layout.addWidget(details_title)

        details_header_layout.addStretch()

        self.export_single_btn = QPushButton("📄 Экспорт")
        self.export_single_btn.setToolTip("Экспортировать отчет")
        self.export_single_btn.clicked.connect(self.export_single_report)
        self.export_single_btn.setEnabled(False)
        self.export_single_btn.setFixedSize(90, 30)
        self.export_single_btn.setFont(QFont("Arial", 9))
        details_header_layout.addWidget(self.export_single_btn)

        right_layout.addWidget(self.details_header)

        self.details_area = QScrollArea()
        self.details_area.setObjectName("detailsArea")
        self.details_area.setWidgetResizable(True)
        self.details_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.details_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.details_container = QWidget()
        self.details_layout = QVBoxLayout(self.details_container)
        self.details_layout.setContentsMargins(15, 15, 15, 15)
        self.details_layout.setSpacing(15)
        self.details_layout.addStretch()

        self.details_area.setWidget(self.details_container)
        right_layout.addWidget(self.details_area, 1)

        self.create_control_panel(right_layout)

        return right_widget

    def create_control_panel(self, parent_layout):
        self.control_panel = QFrame()
        self.control_panel.setObjectName("controlPanel")
        self.control_panel.setFixedHeight(50)

        control_layout = QHBoxLayout(self.control_panel)
        control_layout.setContentsMargins(15, 5, 15, 5)
        control_layout.setSpacing(10)

        self.copy_details_btn = QPushButton("📋 Копировать")
        self.copy_details_btn.setToolTip("Копировать детали в буфер обмена")
        self.copy_details_btn.clicked.connect(self.copy_details)
        self.copy_details_btn.setEnabled(False)
        self.copy_details_btn.setFixedHeight(35)
        self.copy_details_btn.setFont(QFont("Arial", 10))
        control_layout.addWidget(self.copy_details_btn)

        self.delete_entry_btn = QPushButton("🗑️ Удалить")
        self.delete_entry_btn.setToolTip("Удалить выбранную запись")
        self.delete_entry_btn.clicked.connect(self.delete_selected_entry)
        self.delete_entry_btn.setEnabled(False)
        self.delete_entry_btn.setFixedHeight(35)
        self.delete_entry_btn.setFont(QFont("Arial", 10))
        control_layout.addWidget(self.delete_entry_btn)

        control_layout.addStretch()

        parent_layout.addWidget(self.control_panel)

    def create_status_bar(self, parent_layout):
        self.bottom_info = QLabel("© Система верификации подписей")
        self.bottom_info.setObjectName("bottomInfo")
        self.bottom_info.setFixedHeight(30)
        self.bottom_info.setAlignment(Qt.AlignCenter)
        self.bottom_info.setFont(QFont("Arial", 9))
        parent_layout.addWidget(self.bottom_info)

    def check_history_easter_egg_click(self, item):
        """Проверка двойного клика на специальный элемент"""
        if not item:
            return

        text = item.text().lower()
        special_names = ["kashapov", "arsen", "creator"]

        if any(name in text for name in special_names):
            self.show_history_easter_egg_detail()

    def show_history_easter_egg_detail(self):
        """Показ пасхалки при двойном клике"""
        dialog = QDialog(self)
        dialog.setWindowTitle("👑 СЕКРЕТ СОЗДАТЕЛЯ")
        dialog.setFixedSize(500, 400)

        layout = QVBoxLayout(dialog)

        title = QLabel("⚡ КАШАПОВ АРСЕН ⚡")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #f1c40f; padding: 10px;")
        layout.addWidget(title)

        ascii_art = QLabel("""
╔══════════════════════════════╗
║     👨‍💻  M A S T E R  👨‍💻     ║
║                              ║
║    ╱▔▔╲     ╱▔▔╲    ╱▔▔╲    ║
║   ╱    ╲   ╱    ╲  ╱    ╲   ║
║  ╱  🚀  ╲_╱  💻  ╲╱  🧠  ╲  ║
║  ╲______╱╲______╱╲______╱  ║
║                              ║
║    Creator of NeuroSignature ║
╚══════════════════════════════╝
        """)
        ascii_art.setFont(QFont("Courier", 10))
        ascii_art.setAlignment(Qt.AlignCenter)
        layout.addWidget(ascii_art)

        info = QLabel(
            "Эта запись в истории - особенная!\n\n"
            "Кашапов Арсен - создатель NeuroSignature.\n"
            "Он верит, что каждый пользователь может найти\n"
            "что-то особенное в его творении."
        )
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("font-size: 12px; padding: 10px;")
        layout.addWidget(info)

        close_btn = QPushButton("✨ Понятно ✨")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec_()

    def update_theme(self, theme):
        """Обновление темы оформления"""
        self.current_theme = theme

        if theme == "dark":
            self.set_dark_theme_styles()
        else:
            self.set_light_theme_styles()

    def set_light_theme_styles(self):
        self.setStyleSheet("""
            QFrame#topPanel {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
            }

            QFrame#listHeader, QFrame#detailsHeader {
                background-color: #e8e8e8;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
            }

            QFrame#statsPanel, QFrame#controlPanel {
                background-color: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
            }

            QListWidget#historyList {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                outline: none;
                font-size: 11px;
            }

            QListWidget#historyList::item {
                padding: 12px;
                border-bottom: 1px solid #e8e8e8;
                border-radius: 4px;
                margin: 2px;
                background-color: #f8f9fa;
                color: #333333;
            }

            QListWidget#historyList::item:selected {
                background-color: #e3f2fd;
                border: 1px solid #2196f3;
            }

            QListWidget#historyList::item:hover {
                background-color: #e8e8e8;
            }

            QScrollArea#detailsArea {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                background-color: #ffffff;
            }

            QLabel#bottomInfo {
                color: #999999;
                border-top: 1px solid #d0d0d0;
            }

            QPushButton {
                background-color: #e0e0e0;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px 10px;
            }

            QPushButton:hover {
                background-color: #d0d0d0;
                border-color: #2196f3;
            }

            QPushButton:pressed {
                background-color: #c0c0c0;
            }

            QPushButton:disabled {
                background-color: #f0f0f0;
                color: #999999;
                border-color: #dddddd;
            }

            QScrollBar:vertical {
                border: none;
                background-color: #f0f0f0;
                width: 10px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 5px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }

            QSplitter::handle {
                background-color: #d0d0d0;
                border-radius: 2px;
            }

            QSplitter::handle:hover {
                background-color: #2196f3;
            }
        """)

    def set_dark_theme_styles(self):
        self.setStyleSheet("""
            QFrame#topPanel {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 8px;
            }

            QFrame#listHeader, QFrame#detailsHeader {
                background-color: #34495e;
                border: 1px solid #4a6572;
                border-radius: 6px;
            }

            QFrame#statsPanel, QFrame#controlPanel {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 6px;
            }

            QListWidget#historyList {
                background-color: #1e1e1e;
                border: 1px solid #34495e;
                border-radius: 6px;
                outline: none;
                font-size: 11px;
            }

            QListWidget#historyList::item {
                padding: 12px;
                border-bottom: 1px solid #34495e;
                border-radius: 4px;
                margin: 2px;
                background-color: #2c3e50;
                color: #ecf0f1;
            }

            QListWidget#historyList::item:selected {
                background-color: #3a5068;
                border: 1px solid #4a6572;
            }

            QListWidget#historyList::item:hover {
                background-color: #3a5068;
            }

            QScrollArea#detailsArea {
                border: 1px solid #34495e;
                border-radius: 6px;
                background-color: #1e1e1e;
            }

            QLabel#bottomInfo {
                color: #7f8c8d;
                border-top: 1px solid #34495e;
            }

            QPushButton {
                background-color: #34495e;
                color: white;
                border: 1px solid #4a6572;
                border-radius: 4px;
                padding: 5px 10px;
            }

            QPushButton:hover {
                background-color: #4a6572;
                border-color: #5d7b8a;
            }

            QPushButton:pressed {
                background-color: #2c3e50;
            }

            QPushButton:disabled {
                background-color: #2c3e50;
                color: #7f8c8d;
                border-color: #34495e;
            }

            QScrollBar:vertical {
                border: none;
                background-color: #2c3e50;
                width: 10px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background-color: #4a6572;
                border-radius: 5px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #5d7b8a;
            }

            QSplitter::handle {
                background-color: #4a6572;
                border-radius: 2px;
            }

            QSplitter::handle:hover {
                background-color: #5d7b8a;
            }
        """)

    def calculate_item_size(self, text):
        lines = text.strip().split('\n')
        line_count = len([line for line in lines if line.strip()])

        base_height = 90
        line_height = 18
        extra_height = max(0, (line_count - 4) * line_height)

        return QSize(250, base_height + extra_height)

    def update_history_display(self):
        self.history_list.clear()

        if not self.history_data:
            empty_item = QListWidgetItem("📭 История пуста\n\nНажмите 'Обновить' для проверки")
            empty_item.setTextAlignment(Qt.AlignCenter)
            empty_item.setFont(QFont("Arial", 11))
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsSelectable)

            if self.current_theme == "dark":
                empty_item.setForeground(QColor("#95a5a6"))
                empty_item.setBackground(QColor("#2c3e50"))
            else:
                empty_item.setForeground(QColor("#999999"))
                empty_item.setBackground(QColor("#f8f9fa"))

            empty_item.setSizeHint(QSize(250, 120))
            self.history_list.addItem(empty_item)
            self.entries_count.setText("0")
            return

        sorted_data = sorted(self.history_data,
                             key=lambda x: x.get('timestamp', ''),
                             reverse=True)

        for entry in sorted_data:
            timestamp = entry.get('timestamp', 'Нет времени')
            image_name = entry.get('image_name', 'Неизвестный файл')
            processing_type = entry.get('processing_type', 'Неизвестный тип')

            if " vs " in str(image_name):
                files = str(image_name).split(" vs ")
                file1 = files[0][:20] + "..." if len(files[0]) > 20 else files[0]
                file2 = files[1][:20] + "..." if len(files[1]) > 20 else files[1] if len(files) > 1 else "N/A"

                display_text = f"""⚖️ {processing_type}
────────────────
📅 {timestamp}

📄 {file1}
📄 {file2}"""
            else:
                display_name = image_name[:25] + "..." if len(image_name) > 25 else image_name
                display_text = f"""🔍 {processing_type}
────────────
📅 {timestamp}

📄 {display_name}"""

            item = QListWidgetItem(display_text)
            item.setFont(QFont("Arial", 10))
            item.setData(Qt.UserRole, entry.get('id'))
            item.setSizeHint(self.calculate_item_size(display_text))

            self.history_list.addItem(item)

        self.update_stats()
        self.entries_count.setText(str(len(self.history_data)))

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

        self.clear_details_layout()

        full_result = entry.get('full_result', '')

        self.create_detail_card(
            "📋 ИНФОРМАЦИЯ О ЗАПИСИ",
            [
                f"ID: #{entry['id']:04d}",
                f"Дата: {entry['timestamp']}",
                f"Тип: {entry['processing_type']}"
            ]
        )

        image_name = entry.get('image_name', '')
        files_info = []
        if " vs " in str(image_name):
            files = str(image_name).split(" vs ")
            files_info = [
                f"📄 Эталон: {files[0] if len(files) > 0 else 'N/A'}",
                f"📄 Проверяемая: {files[1] if len(files) > 1 else 'N/A'}"
            ]
        else:
            files_info = [f"📄 Файл: {image_name}"]

        self.create_detail_card("📁 ИСХОДНЫЕ ДАННЫЕ", files_info)

        results = []
        lines = full_result.split('\n')
        for line in lines:
            line = line.strip()
            if line and any(key in line for key in ['ВЕРДИКТ:', 'СТЕПЕНЬ СХОДСТВА:', 'УВЕРЕННОСТЬ:']):
                results.append(line)

        if results:
            self.create_detail_card("📊 РЕЗУЛЬТАТЫ", results, is_result=True)

        self.copy_details_btn.setEnabled(True)
        self.delete_entry_btn.setEnabled(True)
        self.export_single_btn.setEnabled(True)

    def create_detail_card(self, title, items, is_result=False):
        card = QFrame()
        card.setObjectName("detailCard")

        if self.current_theme == "dark":
            card.setStyleSheet("""
                QFrame#detailCard {
                    background-color: #2c3e50;
                    border: 1px solid #34495e;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
        else:
            card.setStyleSheet("""
                QFrame#detailCard {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11, QFont.Bold))
        title_label.setStyleSheet("color: #2196f3;" if not self.current_theme == "dark" else "color: #64b5f6;")
        card_layout.addWidget(title_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(
            "background-color: #e0e0e0;" if not self.current_theme == "dark" else "background-color: #34495e;")
        separator.setFixedHeight(1)
        card_layout.addWidget(separator)

        for item in items:
            label = QLabel(item)
            label.setWordWrap(True)
            label.setFont(QFont("Arial", 10))

            if is_result and "ВЕРДИКТ:" in item:
                if "ПОДЛИННАЯ" in item or "СХОДНЫ" in item:
                    label.setStyleSheet("color: #4caf50; font-weight: bold;")
                elif "ПОДДЕЛЬНАЯ" in item or "РАЗЛИЧАЮТСЯ" in item:
                    label.setStyleSheet("color: #f44336; font-weight: bold;")
                else:
                    label.setStyleSheet("color: #ff9800; font-weight: bold;")

            card_layout.addWidget(label)

        self.details_layout.insertWidget(self.details_layout.count() - 1, card)

    def clear_details_layout(self):
        while self.details_layout.count() > 1:
            item = self.details_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def clear_details(self):
        self.clear_details_layout()
        self.copy_details_btn.setEnabled(False)
        self.delete_entry_btn.setEnabled(False)
        self.export_single_btn.setEnabled(False)

    def copy_details(self):
        text_parts = []

        for i in range(self.details_layout.count() - 1):
            item = self.details_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QFrame):
                    for child in widget.findChildren(QLabel):
                        text = child.text()
                        if text and not text.startswith("📋") and not text.startswith("📁") and not text.startswith("📊"):
                            text_parts.append(text)

        if text_parts:
            full_text = "\n".join(text_parts)
            QApplication.clipboard().setText(full_text)
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage("Детали скопированы в буфер обмена")

    def update_stats(self):
        total_entries = len(self.history_data)

        file_size = 0
        if os.path.exists(self.history_file):
            file_size = os.path.getsize(self.history_file)

        size_kb = file_size / 1024
        size_mb = size_kb / 1024

        if size_mb >= 1:
            size_text = f"{size_mb:.2f} MB"
        else:
            size_text = f"{size_kb:.1f} KB"

        self.stats_label.setText(f"{total_entries} записей")
        self.size_label.setText(size_text)

    def load_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history_data = json.load(f)
            else:
                self.history_data = []

            self.update_history_display()
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage("История обновлена")

        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage("Ошибка загрузки истории")

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
                'result_preview': result[:100] + "..." if len(result) > 100 else result,
                'full_result': result
            }

            self.history_data.append(history_entry)
            self.save_history()
            self.update_history_display()

            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(f"Добавлена запись в историю: {processing_type}")

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
            "Удалить выбранную запись?\n\nЭто действие нельзя отменить.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.history_data = [e for e in self.history_data if e.get('id') != entry_id]

            for i, entry in enumerate(self.history_data, 1):
                entry['id'] = i

            self.save_history()
            self.update_history_display()
            self.clear_details()
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage("Запись удалена")

    def clear_all_history(self):
        if not self.history_data:
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение очистки",
            "Очистить всю историю?\n\n"
            "Будет удалено {} записей. Это действие нельзя отменить.".format(len(self.history_data)),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.history_data = []
            self.save_history()
            self.update_history_display()
            self.clear_details()
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage("История очищена")

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
        default_name = f"Отчет_{entry_id:04d}_{timestamp}.txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт отчета",
            default_name,
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write(" " * 20 + "ОТЧЕТ О ПРОВЕРКЕ\n")
                f.write("=" * 60 + "\n\n")

                f.write(f"ID записи: {entry_id:04d}\n")
                f.write(f"Дата проверки: {entry['timestamp']}\n")
                f.write(f"Тип операции: {entry['processing_type']}\n")
                f.write("-" * 60 + "\n\n")

                f.write("ИСХОДНЫЕ ДАННЫЕ:\n")
                f.write("-" * 60 + "\n")
                f.write(f"Файл(ы): {entry['image_name']}\n\n")

                f.write("РЕЗУЛЬТАТЫ:\n")
                f.write("-" * 60 + "\n")
                f.write(entry.get('full_result', 'Нет данных'))
                f.write("\n\n")

                f.write("=" * 60 + "\n")
                f.write("Конец отчета\n")
                f.write("=" * 60 + "\n")

            QMessageBox.information(
                self,
                "Успех",
                f"Отчет успешно экспортирован:\n{os.path.basename(file_path)}"
            )

            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage(f"Экспортирован отчет: {os.path.basename(file_path)}")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось экспортировать отчет:\n{str(e)}"
            )

    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(f"Ошибка: {message}")

    def on_window_resized(self):
        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            if item and item.text() != "📭 История пуста\n\nНажмите 'Обновить' для проверки":
                item.setSizeHint(self.calculate_item_size(item.text()))

        width = self.width()
        if width > 0:
            self.splitter.setSizes([int(width * 0.4), int(width * 0.6)])

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.on_window_resized()
        return super().eventFilter(obj, event)