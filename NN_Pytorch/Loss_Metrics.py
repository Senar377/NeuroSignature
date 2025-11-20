import torch
import torch.nn as nn
import numpy as np

class AdaptiveContrastiveLoss(nn.Module):
    """Комбинированная потеря для стабильного обучения ViT"""
    def __init__(self, margin=0.5, alpha=0.7):
        super().__init__()
        self.margin = margin
        self.alpha = alpha
        self.bce_loss = nn.BCELoss()
    
    def forward(self, output, target):
        # Основная BCE потеря
        bce = self.bce_loss(output, target)
        
        # Адаптивная контрастивная потеря
        positive_mask = (target == 1)
        negative_mask = (target == 0)
        
        pos_loss = 0
        neg_loss = 0
        
        if torch.any(positive_mask):
            pos_diff = torch.clamp(1 - output[positive_mask], min=0)
            pos_loss = torch.mean(pos_diff ** 2)
        
        if torch.any(negative_mask):
            neg_diff = torch.clamp(output[negative_mask] - self.margin, min=0)
            neg_loss = torch.mean(neg_diff ** 2)
        
        contrastive = (pos_loss + neg_loss) / 2
        
        return self.alpha * bce + (1 - self.alpha) * contrastive
    

def calculate_metrics(outputs, targets, threshold=0.5):
    # Вычисление метрик
    preds = (outputs > threshold).float()
    targets = targets.float()
    
    tp = torch.sum((preds == 1) & (targets == 1)).item()
    tn = torch.sum((preds == 0) & (targets == 0)).item()
    fp = torch.sum((preds == 1) & (targets == 0)).item()
    fn = torch.sum((preds == 0) & (targets == 1)).item()
    
    accuracy = (tp + tn) / (tp + tn + fp + fn + 1e-8)
    precision = tp / (tp + fp + 1e-8)
    recall = tp / (tp + fn + 1e-8)
    f1 = 2 * (precision * recall) / (precision + recall + 1e-8)
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn
    }

def create_confusion_matrix(outputs, targets, threshold=0.5):
    # Создание матрицы ошибок
    preds = (outputs > threshold).float()
    targets = targets.float()
    
    tp = torch.sum((preds == 1) & (targets == 1)).item()
    tn = torch.sum((preds == 0) & (targets == 0)).item()
    fp = torch.sum((preds == 1) & (targets == 0)).item()
    fn = torch.sum((preds == 0) & (targets == 1)).item()
    
    return np.array([[tn, fp], [fn, tp]])
