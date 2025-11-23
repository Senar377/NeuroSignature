import os
import glob


def find_model_files():
    """Найти все файлы моделей в проекте"""
    print("Поиск файлов моделей...")

    # Возможные расширения моделей
    extensions = ['*.pth', '*.pt', '*.pkl', '*.onnx']

    model_files = []
    for ext in extensions:
        model_files.extend(glob.glob(f"**/{ext}", recursive=True))
        model_files.extend(glob.glob(f"../**/{ext}", recursive=True))

    if model_files:
        print("Найдены файлы моделей:")
        for i, model_file in enumerate(model_files, 1):
            print(f"{i}. {model_file} (полный путь: {os.path.abspath(model_file)})")
    else:
        print("Файлы моделей не найдены!")

    return model_files


if __name__ == "__main__":
    find_model_files()
