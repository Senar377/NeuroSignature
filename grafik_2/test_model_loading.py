import os
import sys

# Добавляем путь к Gui
sys.path.append('Gui')

from Gui.model_handler import SignatureAnalyzer


def test_model_loading():
    print("🧪 Тестирование загрузки модели...")

    # Создаем анализатор
    analyzer = SignatureAnalyzer()

    print("\n📊 Результаты тестирования:")
    print(f"Модель загружена: {'✅ ДА' if analyzer.model_path else '❌ НЕТ'}")
    if analyzer.model_path:
        print(f"Путь к модели: {analyzer.model_path}")
        print(f"Полный путь: {os.path.abspath(analyzer.model_path)}")
        print(f"Файл существует: {'✅ ДА' if os.path.exists(analyzer.model_path) else '❌ НЕТ'}")
    else:
        print("❌ Модель не загружена!")


if __name__ == "__main__":
    test_model_loading()
