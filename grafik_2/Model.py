import torch
import torch.nn as nn
import torch.nn.functional as F
from einops import rearrange, repeat


class PatchEmbedding(nn.Module):
    def __init__(self, img_size=(128, 256), patch_size=(16, 32), in_chans=1, embed_dim=256):
        super().__init__()
        self.img_height, self.img_width = img_size
        self.patch_height, self.patch_width = patch_size
        
        # Количество патчей по высоте и ширине
        self.num_patches_h = self.img_height // self.patch_height
        self.num_patches_w = self.img_width // self.patch_width
        self.num_patches = self.num_patches_h * self.num_patches_w
        
        # Проекция патчей
        self.proj = nn.Conv2d(
            in_chans, 
            embed_dim, 
            kernel_size=(self.patch_height, self.patch_width),
            stride=(self.patch_height, self.patch_width)
        )
        
        # Позиционное кодирование
        self.pos_embed = nn.Parameter(
            torch.zeros(1, self.num_patches, embed_dim)
        )
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        self._init_weights()
        
    def _init_weights(self):
        nn.init.normal_(self.cls_token, std=0.02)
        nn.init.normal_(self.pos_embed, std=0.02)
        
    def forward(self, x):
        # x: [B, C, H, W]
        B = x.shape[0]
        
        # Проекция патчей
        x = self.proj(x)  # [B, embed_dim, num_patches_h, num_patches_w]
        x = rearrange(x, 'b d h w -> b (h w) d')  # [B, num_patches, embed_dim]
        
        # Добавление позиционного кодирования
        x = x + self.pos_embed.to(x.device)
        
        # Добавление CLS token
        cls_tokens = repeat(self.cls_token, '1 1 d -> b 1 d', b=B)
        x = torch.cat([cls_tokens, x], dim=1)  # [B, 1+num_patches, embed_dim]
        
        return x

class TransformerBlock(nn.Module):
    def __init__(self, dim, num_heads, mlp_ratio=4.0, dropout=0.1):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim)
        self.attn = nn.MultiheadAttention(
            dim, num_heads, dropout=dropout, batch_first=True
        )
        self.norm2 = nn.LayerNorm(dim)
        self.mlp = nn.Sequential(
            nn.Linear(dim, int(dim * mlp_ratio)),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(int(dim * mlp_ratio), dim),
            nn.Dropout(dropout)
        )
        
    def forward(self, x):
        # Self-attention
        attn_output, _ = self.attn(
            self.norm1(x), 
            self.norm1(x), 
            self.norm1(x)
        )
        x = x + attn_output
        
        # MLP
        x = x + self.mlp(self.norm2(x))
        return x

class SignatureViT(nn.Module):
    def __init__(self, img_size=(128, 256), patch_size=(16, 32), 
                 in_chans=1, embed_dim=256, depth=6, num_heads=8, 
                 mlp_ratio=4.0, dropout=0.1):
        super().__init__()
        self.patch_embed = PatchEmbedding(
            img_size=img_size,
            patch_size=patch_size,
            in_chans=in_chans,
            embed_dim=embed_dim
        )
        
        # Transformer encoder
        self.blocks = nn.ModuleList([
            TransformerBlock(
                dim=embed_dim,
                num_heads=num_heads,
                mlp_ratio=mlp_ratio,
                dropout=dropout
            ) for _ in range(depth)
        ])
        
        self.norm = nn.LayerNorm(embed_dim)
        self.dropout = nn.Dropout(dropout)
        
        # Размер выходного вектора: [CLS token + среднее по патчам]
        self.feature_dim = embed_dim * 2
        
    def forward(self, x):
        # x: [B, 1, 128, 256]
        B = x.shape[0]
        
        # Разбиение на патчи и добавление CLS token
        x = self.patch_embed(x)  # [B, 1+num_patches, embed_dim]
        
        # Transformer encoder
        for block in self.blocks:
            x = block(x)
        
        x = self.norm(x)
        
        # Извлекаем CLS token как глобальное представление
        cls_features = x[:, 0]  # [B, embed_dim]
        
        # Также используем среднее по всем патчам для дополнительной информации
        patch_features = x[:, 1:].mean(dim=1)  # [B, embed_dim]
        
        # Комбинируем оба представления
        combined_features = torch.cat([cls_features, patch_features], dim=1)  # [B, 2*embed_dim]
        
        return combined_features


class SignatureFeatureExtractor(nn.Module):
    def __init__(self):
        super().__init__()
        # Вход: [1, 128, 256]
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=5, stride=2, padding=2),  # [32, 64, 128]
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2)  # [32, 32, 64]
        )
        
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),  # [64, 32, 64]
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2)  # [64, 16, 32]
        )
        
        self.conv3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),  # [128, 16, 32]
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2)  # [128, 8, 16]
        )
        
        self.conv4 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),  # [256, 8, 16]
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 8))  # [256, 4, 8]
        )
        
        # Полносвязные слои
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 4 * 8, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 512)
        )
        
    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = self.fc(x)
        return x



class SiameseViT(nn.Module):
    def __init__(self, feature_dim=512, embed_dim=256, dropout=0.3, img_size=(128, 256), patch_size=(16, 32)):
        super().__init__()
        # Общий экстрактор признаков
        self.feature_extractor = SignatureViT(
            img_size=img_size,
            patch_size=patch_size,  # Оптимально для вытянутых подписей
            embed_dim=embed_dim,
            depth=6,
            num_heads=8
        )
        
        self.conv_feature_extractor = SignatureFeatureExtractor()

        
        # Специализированный компаратор с учетом асимметрии
        input_dim = embed_dim * 2 * 6  # 6 типа взаимодействий
        
        self.asymmetric_comparator = nn.Sequential(
            nn.Linear(input_dim, feature_dim),
            nn.LayerNorm(feature_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            
            nn.Linear(feature_dim, feature_dim // 2),
            nn.LayerNorm(feature_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            
            nn.Linear(feature_dim // 2, 1)
        )
        
        self._init_weights()
    
    def _init_weights(self):
        for module in self.asymmetric_comparator.modules():
            if isinstance(module, nn.Linear):
                nn.init.kaiming_normal_(module.weight, nonlinearity='relu')
                nn.init.zeros_(module.bias)
    
    def forward(self, img1, img2):
        # Извлекаем признаки для обоих изображений
        feat1 = self.feature_extractor(img1)  # [B, 512]
        feat2 = self.feature_extractor(img2)  # [B, 512]
        feat1_conv = self.conv_feature_extractor(img1) # [B, 512]
        feat2_conv = self.conv_feature_extractor(img2) # [B, 512]
        
        
        # Асимметричное сравнение
        diff = torch.abs(feat1 - feat2)       # Разница признаков
        prod = feat1 * feat2                  # Элементное умножение
        ratio = feat2 / (feat1 + 1e-8)        # Относительное соотношение
        
        # Объединяем все типы сравнений
        combined = torch.cat([
            feat1,        # Признаки оригинала
            feat2,        # Признаки проверяемой
            feat1_conv,
            feat2_conv,
            diff,         # Абсолютная разница
            prod * ratio  # Комбинированная мера
        ], dim=1)         # [B, 4*512]
        
        # Классификация
        output = self.asymmetric_comparator(combined)
        return torch.sigmoid(output).squeeze()  # [B]