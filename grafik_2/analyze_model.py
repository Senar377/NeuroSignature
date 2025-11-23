import torch
import os


def analyze_model_structure():
    """Анализирует структуру сохраненной модели"""
    model_path = "models/best_model.pth"

    if not os.path.exists(model_path):
        print("❌ Файл модели не найден!")
        return

    print("🔍 Анализ структуры модели...")
    checkpoint = torch.load(model_path, map_location='cpu')

    print("📋 Все ключи в checkpoint:")
    for key in checkpoint.keys():
        print(f"   - {key}: {type(checkpoint[key])}")

    if 'model_state_dict' in checkpoint:
        state_dict = checkpoint['model_state_dict']
        print(f"\n📊 Количество параметров в model_state_dict: {len(state_dict)}")

        # Анализируем размеры параметров
        print("\n📐 Размеры ключевых параметров:")
        for key in list(state_dict.keys())[:20]:  # Покажем первые 20
            if 'weight' in key or 'bias' in key:
                print(f"   - {key}: {state_dict[key].shape}")

        # Ищем параметры asymmetric_comparator
        print("\n🔎 Параметры asymmetric_comparator:")
        for key in state_dict.keys():
            if 'asymmetric_comparator' in key:
                print(f"   - {key}: {state_dict[key].shape}")

    # Анализируем метрики
    if 'f1' in checkpoint:
        print(f"\n🏆 Метрики модели:")
        print(f"   - F1 Score: {checkpoint['f1']:.4f}")
        print(f"   - Epoch: {checkpoint.get('epoch', 'N/A')}")

    if 'metrics' in checkpoint:
        print(f"   - Metrics: {checkpoint['metrics']}")


if __name__ == "__main__":
    analyze_model_structure()
