import torch
import torchvision.transforms as transforms
from PIL import Image
import matplotlib.pyplot as plt
from Model import SiameseViT

# Определение устройства
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def verify_signature(model, img1_path, img2_path, transform, device, show_result=True):
    try:
        model.eval()

        # Загрузка изображений
        img1 = Image.open(img1_path).convert('L')
        img2 = Image.open(img2_path).convert('L')

        # Применение преобразований
        img1_tensor = transform(img1).unsqueeze(0).to(device)
        img2_tensor = transform(img2).unsqueeze(0).to(device)

        # Предсказание
        with torch.no_grad():
            output = model(img1_tensor, img2_tensor)

        confidence = output.item()
        result = True if confidence > 0.5 else False

        if show_result:
            # Визуализация
            result_txt = "Оригинал" if result else "Подделка"
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            ax1.imshow(img1, cmap='gray')
            ax1.set_title(f"Оригинальная подпись")
            ax1.axis('off')

            ax2.imshow(img2, cmap='gray')
            color = 'green' if result else 'red'
            ax2.set_title(f"Результат: {result_txt}\\nПроцент оригинальности: {confidence * 100:.2f}%", color=color,
                          fontsize=14)
            ax2.axis('off')

            plt.tight_layout()
            plt.show()

        return result, confidence

    except Exception as e:
        print(f"Ошибка в verify_signature: {str(e)}")
        return False, 0.0  # Всегда возвращаем значения по умолчанию


def signature_recognition(img_orig, img_test, model_path):
    try:
        img_size = (128, 256)

        # Создание модели
        model = SiameseViT(feature_dim=1024, embed_dim=256, img_size=img_size).to(device)

        # Загрузка весов модели
        checkpoint = torch.load(model_path, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])

        # Преобразования
        transform = transforms.Compose([
            transforms.Resize(img_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])

        # Проверка подписи
        result, confidence = verify_signature(
            model,
            img_orig,
            img_test,
            transform,
            device,
            show_result=False
        )

        return result, confidence

    except Exception as e:
        print(f"Ошибка при проверке: {str(e)}")
        return False, 0.0  # Всегда возвращаем корректные значения вместо None
