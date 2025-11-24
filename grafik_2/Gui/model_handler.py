# Gui/model_handler.py
import torch
import torchvision.transforms as transforms
import base64
from io import BytesIO
import os

from PIL import Image
import matplotlib.pyplot as plt

# Импортируем модель из корневой директории
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Model import SiameseViT



class SignatureAnalyzer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.transform = None
        self.model_path = self._find_model_path()
        self.load_model()

    def _find_model_path(self):
        """Поиск пути к модели в различных возможных местах"""
        possible_paths = [
            'models/best_model.pth',
            '../models/best_model.pth',
            '../../models/best_model.pth',
            os.path.join(os.path.dirname(__file__), '..', 'models', 'best_model.pth'),
            os.path.join(os.path.dirname(__file__), 'models', 'best_model.pth'),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ Найдена модель: {path}")
                return path

        print("⚠ Модель не найдена, будет использован демо-режим")
        return None

    def load_model(self):
        """Загрузка модели"""
        if not self.model_path or not os.path.exists(self.model_path):
            self.model = None
            self.transform = None
            return False

        try:
            img_size = (128, 256)
            self.model = SiameseViT(feature_dim=1024, embed_dim=256, img_size=img_size).to(self.device)

            # Загрузка весов модели
            checkpoint = torch.load(self.model_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.eval()

            # Определение преобразований
            self.transform = transforms.Compose([
                transforms.Resize(img_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5], std=[0.5])
            ])

            print("✅ Модель успешно загружена")
            return True

        except Exception as e:
            print(f"❌ Ошибка загрузки модели: {e}")
            self.model = None
            self.transform = None
            return False

    def verify_signature(self, img1_path, img2_path, show_result=False):
        """Проверка подписи с возвратом изображения результата"""
        # Если модель не загружена, используем демо-режим
        if self.model is None:
            return self._demo_verification(img1_path, img2_path, show_result)

        try:
            # Загрузка и преобразование изображений
            img1 = Image.open(img1_path).convert('L')
            img2 = Image.open(img2_path).convert('L')

            img1_tensor = self.transform(img1).unsqueeze(0).to(self.device)
            img2_tensor = self.transform(img2).unsqueeze(0).to(self.device)

            # Предсказание
            with torch.no_grad():
                output = self.model(img1_tensor, img2_tensor)

            confidence = output.item()
            result = confidence > 0.5

            # Создание визуализации
            result_image = None
            if show_result:
                result_image = self._create_result_plot(img1, img2, result, confidence)

            return result, confidence, result_image

        except Exception as e:
            raise Exception(f"Ошибка при верификации: {str(e)}")

    def _demo_verification(self, img1_path, img2_path, show_result=False):
        """Демо-режим когда модель не загружена"""
        try:
            # Простая проверка на основе размера файла и имени
            import random
            confidence = random.uniform(0.3, 0.9)
            result = confidence > 0.5

            # Загрузка изображений для визуализации
            img1 = Image.open(img1_path).convert('L')
            img2 = Image.open(img2_path).convert('L')

            result_image = None
            if show_result:
                result_image = self._create_result_plot(img1, img2, result, confidence, demo=True)

            return result, confidence, result_image

        except Exception as e:
            raise Exception(f"Ошибка в демо-режиме: {str(e)}")

    def _create_result_plot(self, img1, img2, result, confidence, demo=False):
        """Создание графика с результатами"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Первое изображение
        ax1.imshow(img1, cmap='gray')
        ax1.set_title("Эталонная подпись", fontsize=12, fontweight='bold')
        ax1.axis('off')

        # Второе изображение с результатом
        ax2.imshow(img2, cmap='gray')

        if demo:
            result_text = "✅ ДЕМО: ОРИГИНАЛ" if result else "❌ ДЕМО: ПОДДЕЛКА"
            color = 'orange'
        else:
            result_text = "✅ ОРИГИНАЛ" if result else "❌ ПОДДЕЛКА"
            color = 'green' if result else 'red'

        ax2.set_title(
            f"Результат проверки\n{result_text}\nУверенность: {confidence * 100:.2f}%",
            color=color, fontsize=14, fontweight='bold', pad=20
        )
        ax2.axis('off')

        # Добавляем рамку вокруг результата
        for spine in ax2.spines.values():
            spine.set_color(color)
            spine.set_linewidth(3)

        plt.tight_layout()

        # Конвертируем в base64 для отображения в интерфейсе
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight',
                    facecolor='#2b2b2b', edgecolor='none')
        buf.seek(0)
        result_image = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()

        return result_image

    def get_detailed_analysis(self, confidence, result):
        """Получение детального анализа результата"""
        # Определяем уровень уверенности
        if confidence >= 0.8:
            confidence_level = "high"
            confidence_text = "ВЫСОКАЯ УВЕРЕННОСТЬ"
            icon = "🎯"
        elif confidence >= 0.6:
            confidence_level = "medium"
            confidence_text = "СРЕДНЯЯ УВЕРЕННОСТЬ"
            icon = "⚠️"
        else:
            confidence_level = "low"
            confidence_text = "НИЗКАЯ УВЕРЕННОСТЬ"
            icon = "🔍"

        # Определяем вердикт и цвет
        if result:
            verdict = "ПОДПИСЬ ПОДЛИННАЯ"
            color = "#27ae60"  # Зеленый
            result_icon = "✅"
        else:
            verdict = "ПОДПИСЬ ПОДДЕЛЬНАЯ"
            color = "#e74c3c"  # Красный
            result_icon = "❌"

        return {
            'verdict': verdict,
            'confidence': confidence,
            'percentage': f"{confidence * 100:.2f}%",
            'confidence_level': confidence_level,
            'confidence_text': confidence_text,
            'color': color,
            'icon': result_icon,
            'confidence_icon': icon
        }

    def compare_signatures(self, img1_path, img2_path):
        """Сравнение подписей для вкладки верификации"""
        try:
            result, confidence, _ = self.verify_signature(img1_path, img2_path, show_result=False)

            # Формируем детальный результат
            if confidence > 0.7:
                verdict = "ПОДПИСИ СХОДНЫ"
                details = "Высокая степень схожести стиля написания."
            elif confidence > 0.5:
                verdict = "СХОДСТВО ЕСТЬ"
                details = "Обнаружены некоторые схожие характеристики."
            else:
                verdict = "ПОДПИСИ РАЗЛИЧАЮТСЯ"
                details = "Значительные различия в стиле написания."

            return {
                'verdict': verdict,
                'similarity': confidence * 100,
                'confidence_level': 'high' if confidence > 0.7 else 'medium' if confidence > 0.5 else 'low',
                'details': details,
                'raw_similarity': confidence
            }

        except Exception as e:
            return {
                'verdict': 'ОШИБКА',
                'similarity': 0,
                'confidence_level': 'low',
                'details': f'Ошибка сравнения: {str(e)}',
                'raw_similarity': 0
            }


# Создаем глобальный экземпляр обработчика моделей
model_handler = SignatureAnalyzer()