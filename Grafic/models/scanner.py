import torch
import torchvision.transforms as transforms
from PIL import Image
import json
import os
from datetime import datetime

from Grafic.models.Model import SiameseViT


class SignatureScanner:
    def __init__(self, config):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.transform = None
        self.history_file = "scan_history.json"
        self.load_model()

    def load_model(self):
        """Загрузка модели"""
        try:
            model_path = "models/best_model.pth"
            img_size = tuple(self.config['model_settings']['img_size'])

            self.model = SiameseViT(
                feature_dim=1024,
                embed_dim=256,
                img_size=img_size
            ).to(self.device)

            # Загрузка весов модели
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.eval()

            # Преобразования для изображений
            self.transform = transforms.Compose([
                transforms.Resize(img_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5], std=[0.5])
            ])

            print(f"Модель загружена успешно на устройство: {self.device}")

        except Exception as e:
            raise Exception(f"Ошибка загрузки модели: {str(e)}")

    def verify_signatures(self, original_path, test_path):
        """Проверка подписей"""
        try:
            # Загрузка изображений
            img1 = Image.open(original_path).convert('L')
            img2 = Image.open(test_path).convert('L')

            # Применение преобразований
            img1_tensor = self.transform(img1).unsqueeze(0).to(self.device)
            img2_tensor = self.transform(img2).unsqueeze(0).to(self.device)

            # Предсказание
            with torch.no_grad():
                output = self.model(img1_tensor, img2_tensor)

            confidence = output.item()
            threshold = self.config['scanner_settings']['confidence_threshold']
            result = confidence > threshold

            return result, confidence

        except Exception as e:
            raise Exception(f"Ошибка при проверке подписей: {str(e)}")

    def save_to_history(self, original_path, test_path, result, confidence):
        """Сохранение результата в историю"""
        try:
            history_data = []

            # Загрузка существующей истории
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)

            # Добавление новой записи
            new_record = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'original_path': original_path,
                'test_path': test_path,
                'result': result,
                'confidence': confidence
            }

            history_data.append(new_record)

            # Сохранение (ограничиваем историю последними 100 записями)
            history_data = history_data[-100:]

            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Ошибка сохранения в историю: {str(e)}")
