import torch
from Grafic.models.Model import SiameseViT


class ModelLoader:
    @staticmethod
    def load_model(model_path, img_size=(128, 256), device=None):
        """Загрузка модели из файла"""
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        model = SiameseViT(
            feature_dim=1024,
            embed_dim=256,
            img_size=img_size
        ).to(device)

        checkpoint = torch.load(model_path, map_location=device, weights_only=False)
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()

        return model
