import os
import sys
import random
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QFileDialog, QWidget, QTextEdit,
                               QMessageBox, QScrollArea, QSizePolicy, QFrame,
                               QTabWidget, QStatusBar, QMenuBar, QMenu, QProgressBar,
                               QDialog)
from PySide6.QtCore import Qt, QTimer, QSettings, QPropertyAnimation, QPoint
from PySide6.QtGui import QFont, QAction, QKeySequence, QShortcut


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("NeuroSignature", "AppSettings")
        self.current_theme = "light"
        self.click_count = 0
        self.easter_eggs_found = []
        self.setup_ui()
        self.setup_menu()
        self.load_theme_settings()
        self.setup_easter_eggs()

    def setup_ui(self):
        self.setWindowTitle('NeuroSignature - Анализ подписей')
        self.setMinimumSize(1024, 768)
        self.setGeometry(100, 100, 1400, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        try:
            from Gui.verification_tab import VerificationTab
            from Gui.history_tab import HistoryTab
            from Gui.settings_tab import SettingsTab
            from Gui.model_handler import model_handler

            self.verification_tab = VerificationTab(self)
            self.history_tab = HistoryTab(self)
            self.settings_tab = SettingsTab(self)

            self.tab_widget.addTab(self.verification_tab, "🔍 Верификация")
            self.tab_widget.addTab(self.history_tab, "📋 История")
            self.tab_widget.addTab(self.settings_tab, "⚙ Настройки")

        except ImportError as e:
            print(f"Ошибка загрузки вкладок: {e}")
            error_label = QLabel(f"Ошибка загрузки интерфейса: {e}")
            error_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(error_label)

        self.statusBar().showMessage("Готов к работе")

        try:
            if hasattr(model_handler, 'model_path') and model_handler.model_path and os.path.exists(
                    model_handler.model_path):
                model_name = os.path.basename(model_handler.model_path)
                self.statusBar().showMessage(f"✅ Модель загружена: {model_name}")
            else:
                self.statusBar().showMessage("⚠ ДЕМО-РЕЖИМ: Модель не найдена")
        except Exception as e:
            print(f"Ошибка при проверке модели: {e}")
            self.statusBar().showMessage("⚠ Статус модели неизвестен")

    def setup_menu(self):
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu('Файл')

        open_action = QAction('Открыть изображение', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню Вид
        view_menu = menubar.addMenu('Вид')

        history_action = QAction('История', self)
        history_action.setShortcut('F3')
        history_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        view_menu.addAction(history_action)

        settings_action = QAction('Настройки', self)
        settings_action.setShortcut('F4')
        settings_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        view_menu.addAction(settings_action)

        view_menu.addSeparator()

        theme_menu = view_menu.addMenu('Тема оформления')

        light_theme_action = QAction('Светлая', self)
        light_theme_action.triggered.connect(lambda: self.change_theme('light'))
        theme_menu.addAction(light_theme_action)

        dark_theme_action = QAction('Темная', self)
        dark_theme_action.triggered.connect(lambda: self.change_theme('dark'))
        theme_menu.addAction(dark_theme_action)

        # Меню Помощь
        help_menu = menubar.addMenu('Помощь')

        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_easter_eggs(self):
        """Настройка пасхалок"""

        # Пасхалка "KASHAPOV" - комбинация клавиш
        kashapov_shortcut = QShortcut(QKeySequence("Ctrl+Shift+K"), self)
        kashapov_shortcut.activated.connect(self.easter_egg_kashapov)

        # Пасхалка "CREATOR" - для создателя
        creator_shortcut = QShortcut(QKeySequence("Ctrl+Alt+C"), self)
        creator_shortcut.activated.connect(self.easter_egg_creator)

    def easter_egg_kashapov(self):
        """Пасхалка о Кашапове"""
        self.register_easter_egg("Kashapov")

        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.FramelessWindowHint)
        dialog.setStyleSheet("background-color: #2c3e50; border-radius: 15px;")
        dialog.setFixedSize(600, 400)

        layout = QVBoxLayout(dialog)

        self.kashapov_label = QLabel()
        self.kashapov_label.setAlignment(Qt.AlignCenter)
        self.kashapov_label.setFont(QFont("Courier", 12))
        self.kashapov_label.setStyleSheet("color: #00ff00;")
        layout.addWidget(self.kashapov_label)

        self.matrix_text = [
            "К А Ш А П О В   А Р С Е Н",
            "K A S H A P O V   A R S E N",
            "С О З Д А Т Е Л Ь   П Р О Г Р А М М Ы",
            "C R E A T O R   O F   P R O G R A M",
            "Н Е Й Р О С Е Т И   Э Т О   М А Г И Я"
        ]
        self.matrix_index = 0

        self.matrix_timer = QTimer()
        self.matrix_timer.timeout.connect(lambda: self.update_matrix(dialog))
        self.matrix_timer.start(200)

        QTimer.singleShot(5000, dialog.close)
        QTimer.singleShot(5000, self.matrix_timer.stop)

        dialog.exec_()

    def update_matrix(self, dialog):
        """Обновление матричного текста"""
        if hasattr(self, 'kashapov_label'):
            import random
            text = self.matrix_text[self.matrix_index % len(self.matrix_text)]
            matrix_effect = ''.join([c if random.random() > 0.3 else chr(random.randint(65, 90))
                                     for c in text])
            self.kashapov_label.setText(matrix_effect)
            self.matrix_index += 1

    def easter_egg_creator(self):
        """Главная пасхалка о создателе"""
        self.register_easter_egg("Creator")

        dialog = QDialog(self)
        dialog.setWindowTitle("👑 ГЛАВНЫЙ СОЗДАТЕЛЬ")
        dialog.setFixedSize(700, 500)

        layout = QVBoxLayout(dialog)

        title = QLabel("⚡ КАШАПОВ АРСЕН ⚡")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #f1c40f;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #9b59b6);
                border-radius: 10px;
            }
        """)
        layout.addWidget(title)

        photo_label = QLabel()
        photo_label.setFixedSize(200, 200)
        photo_label.setAlignment(Qt.AlignCenter)
        photo_label.setStyleSheet("""
            QLabel {
                border: 5px solid #3498db;
                border-radius: 100px;
                background-color: #ecf0f1;
            }
        """)
        photo_label.setText("👨‍💻")
        photo_label.setFont(QFont("Arial", 80))
        photo_label.setAlignment(Qt.AlignCenter)

        photo_container = QWidget()
        photo_layout = QHBoxLayout(photo_container)
        photo_layout.addStretch()
        photo_layout.addWidget(photo_label)
        photo_layout.addStretch()
        layout.addWidget(photo_container)

        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 15px;
                font-size: 14px;
            }
        """)

        info_text.setHtml("""
        <div style='font-family: Arial;'>
            <h2 style='color: #2c3e50;'>📋 Биография создателя</h2>

            <table style='width:100%; border-collapse: collapse;'>
                <tr>
                    <td style='padding: 10px;'><b>👤 Полное имя:</b></td>
                    <td style='padding: 10px;'>Кашапов Арсен Маратович</td>
                </tr>
                <tr style='background-color: #f0f0f0;'>
                    <td style='padding: 10px;'><b>📍 Местоположение:</b></td>
                    <td style='padding: 10px;'>Россия, Казань</td>
                </tr>
                <tr>
                    <td style='padding: 10px;'><b>💻 Специализация:</b></td>
                    <td style='padding: 10px;'>Deep Learning, Computer Vision, GUI Development</td>
                </tr>
                <tr style='background-color: #f0f0f0;'>
                    <td style='padding: 10px;'><b>🚀 Проекты:</b></td>
                    <td style='padding: 10px;'>NeuroSignature, Neural Networks, AI Systems</td>
                </tr>
                <tr>
                    <td style='padding: 10px;'><b>🎯 Любимые технологии:</b></td>
                    <td style='padding: 10px;'>PyTorch, TensorFlow, Qt, OpenCV</td>
                </tr>
                <tr style='background-color: #f0f0f0;'>
                    <td style='padding: 10px;'><b>⭐️ Достижения:</b></td>
                    <td style='padding: 10px;'>Разработка системы верификации подписей с точностью 94.7%</td>
                </tr>
            </table>

            <hr style='border: 2px solid #3498db; margin: 20px 0;'>

            <h3 style='color: #2c3e50;'>🌟 Интересные факты:</h3>
            <ul>
                <li>Начал программировать в 12 лет на Pascal</li>
                <li>Создал первую нейросеть в 16 лет для распознавания рукописных цифр</li>
                <li>Увлекается компьютерным зрением и обработкой изображений</li>
                <li>Любит решать сложные задачи оптимизации алгоритмов</li>
                <li>Верит, что ИИ изменит мир к лучшему</li>
            </ul>

            <hr style='border: 2px solid #3498db; margin: 20px 0;'>

            <div style='text-align: center; margin-top: 20px;'>
                <i>"Код - это поэзия, а нейросети - это магия, которую мы создаем сами"</i>
                <br><b>© Кашапов Арсен, 2024</b>
            </div>
        </div>
        """)

        layout.addWidget(info_text)

        close_btn = QPushButton("Закрыть")
        close_btn.setFixedHeight(40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec_()

    def register_easter_egg(self, egg_name):
        """Регистрация найденной пасхалки"""
        if egg_name not in self.easter_eggs_found:
            self.easter_eggs_found.append(egg_name)
            self.statusBar().showMessage(f"🥚 Пасхалка '{egg_name}' найдена!")

    def animate_status_bar(self, message):
        """Анимация статус бара"""
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff"]

        def update_color():
            color = random.choice(colors)
            self.statusBar().setStyleSheet(f"QStatusBar{{color: {color}; font-weight: bold;}}")

        for i in range(10):
            QTimer.singleShot(i * 100, update_color)

        self.statusBar().showMessage(message)

        QTimer.singleShot(2000, lambda: self.statusBar().setStyleSheet(""))

    def mousePressEvent(self, event):
        """Отслеживание кликов для пасхалки"""
        super().mousePressEvent(event)

        if event.pos().x() < 50 and event.pos().y() < 50:
            self.click_count += 1

            if self.click_count == 5:
                self.easter_egg_kashapov()
                self.click_count = 0
            elif self.click_count > 0:
                self.statusBar().showMessage(f"Осталось {5 - self.click_count} кликов до пасхалки...")

    def change_theme(self, theme):
        """Смена темы оформления"""
        self.current_theme = theme
        self.apply_theme()
        self.settings.setValue("interface/theme", "Светлая" if theme == "light" else "Темная (по умолчанию)")
        self.settings.sync()

        if hasattr(self, 'settings_tab'):
            self.settings_tab.load_settings()

    def apply_theme(self):
        """Применение выбранной темы"""
        if self.current_theme == 'dark':
            self.set_dark_theme()
        else:
            self.set_light_theme()

        self.update_all_tabs_theme()

    def update_all_tabs_theme(self):
        """Обновление темы во всех вкладках"""
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if hasattr(widget, 'update_theme'):
                widget.update_theme(self.current_theme)

    def load_theme_settings(self):
        """Загрузка настроек темы"""
        saved_theme = self.settings.value("interface/theme", "Светлая")
        if saved_theme == "Темная (по умолчанию)":
            self.current_theme = "dark"
        else:
            self.current_theme = "light"
        self.apply_theme()

    def set_dark_theme(self):
        """Темная тема"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 16px;
                border: 1px solid #555555;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #505050;
                border-color: #0078d7;
            }
            QTabBar::tab:hover {
                background-color: #484848;
            }
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QTextEdit, QListWidget, QLineEdit, QComboBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QLabel {
                color: #ffffff;
            }
            QGroupBox {
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QStatusBar {
                background-color: #353535;
                color: #cccccc;
                border-top: 1px solid #555555;
            }
            QMenuBar {
                background-color: #353535;
                color: #ffffff;
            }
            QMenuBar::item:selected {
                background-color: #505050;
            }
            QMenu {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QMenu::item:selected {
                background-color: #505050;
            }
        """)

    def set_light_theme(self):
        """Светлая тема"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                color: #333333;
            }
            QWidget {
                background-color: #f5f5f5;
                color: #333333;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #333333;
                padding: 8px 16px;
                border: 1px solid #cccccc;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-color: #0078d7;
            }
            QTabBar::tab:hover {
                background-color: #d0d0d0;
            }
            QPushButton {
                background-color: #e0e0e0;
                color: #333333;
                border: 1px solid #cccccc;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
                border-color: #0078d7;
            }
            QTextEdit, QListWidget, QLineEdit, QComboBox {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px;
            }
            QLabel {
                color: #333333;
            }
            QGroupBox {
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #ffffff;
                color: #333333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #0078d7;
            }
            QStatusBar {
                background-color: #e0e0e0;
                color: #666666;
                border-top: 1px solid #cccccc;
            }
            QFrame {
                background-color: #ffffff;
            }
            QMenuBar {
                background-color: #e0e0e0;
                color: #333333;
            }
            QMenuBar::item:selected {
                background-color: #d0d0d0;
            }
            QMenu {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
            }
            QMenu::item:selected {
                background-color: #e0e0e0;
            }
        """)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение подписи",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.gif *.webp);;All Files (*)"
        )
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        """Загрузка изображения в текущую вкладку"""
        current_tab = self.tab_widget.currentWidget()
        if hasattr(current_tab, 'load_image'):
            current_tab.load_image(file_path)
        elif hasattr(current_tab, 'load_reference_image'):
            current_tab.load_reference_image(file_path)

    def show_about(self):
        about_text = """
NeuroSignature - Система анализа и верификации подписей

Версия 2.0

Возможности:
• Анализ качества и характеристик подписей
• Верификация подлинности подписей
• Сравнение двух подписей на схожесть
• Ведение истории обработки

Используемые технологии:
• PySide6 для интерфейса
• PyTorch для нейросетевых моделей
• Компьютерное зрение для анализа изображений

Разработано Кашаповым Арсеном для автоматизации проверки подписей.
"""
        QMessageBox.about(self, "О программе", about_text)

    def update_status(self, message):
        """Обновление статусной строки"""
        self.statusBar().showMessage(message)

    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if hasattr(widget, 'on_window_resized'):
                widget.on_window_resized()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())