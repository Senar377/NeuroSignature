import matplotlib.pyplot as plt
import seaborn as sns

# Настройка matplotlib
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 100
sns.set_style('whitegrid')
sns.set_context('notebook', font_scale=1.2)

def visualize_pair(dataset, idx):
    # Визуализация 2 изображений из датасета
    (img1, img2), label = dataset[idx]
    
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    axs[0].imshow(img1.squeeze(), cmap='gray')
    axs[0].set_title("Оригинальная подпись")
    axs[0].axis('off')
    
    axs[1].imshow(img2.squeeze(), cmap='gray')
    axs[1].set_title(f"Проверяемая подпись\n Класс: {label.item()}")
    axs[1].axis('off')

    plt.tight_layout()
    plt.show()


def plot_training_history(history):
    # Построение графиков истории обучения
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # График потерь
    ax1.plot(history['train_loss'], label='Train Loss', marker='o')
    ax1.plot(history['val_loss'], label='Val Loss', marker='o')
    ax1.set_title('Потери')
    ax1.set_xlabel('Эпоха')
    ax1.set_ylabel('Loss')
    ax1.legend()
    ax1.grid(True)
    
    # График метрик
    ax2.plot(history['train_f1'], label='Train F1', marker='s')
    ax2.plot(history['val_f1'], label='Val F1', marker='s')
    ax2.plot(history['val_precision'], label='Val Precision', marker='^')
    ax2.plot(history['val_recall'], label='Val Recall', marker='v')
    ax2.set_title('Качество метрик')
    ax2.set_xlabel('Эпоха')
    ax2.set_ylabel('Значение метрики')
    ax2.legend()
    ax2.grid(True)
    
    # plt.tight_layout()
    plt.show()

def plot_confusion_matrix(cm):
    # Построение матрицы ошибок
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Подделка', 'Оригинал'],
                yticklabels=['Подделка', 'Оригинал'])
    plt.title('Матрица ошибок')
    plt.ylabel('Истинный класс')
    plt.xlabel('Предсказанный класс')
    # plt.tight_layout()
    plt.show()