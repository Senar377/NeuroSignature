from tqdm import tqdm
import torch
from Grafic.models.Loss_Metrics import calculate_metrics, create_confusion_matrix
from Grafic.models.Visual_func import plot_training_history, plot_confusion_matrix


def train_model(model, total_epochs, train_loader, test_loader,
                warmup_scheduler, main_scheduler, warmup_epochs,
                optimizer, criterion, best_model_path, final_model_path, device, plot_on_train=True):
    print(f"Начало обучения модели на {total_epochs} эпохах")

    # История обучения
    history = {
        'train_loss': [], 'val_loss': [],
        'train_f1': [], 'val_f1': [],
        'val_precision': [], 'val_recall': [],
        'learning_rates': []
    }
    # Лучшие метрики
    best_f1 = 0.0
    best_epoch = 0

    # ОСНОВНОЙ ЦИКЛ ОБУЧЕНИЯ
    for epoch in range(total_epochs):

        # Выбор планировщика
        scheduler = warmup_scheduler if epoch < warmup_epochs else main_scheduler

        # ===== ОБУЧЕНИЕ =====
        model.train()
        total_loss = 0
        all_preds, all_targets = [], []

        # Прогресс-бар для обучения
        train_pbar = tqdm(train_loader, desc=f'Эпоха {epoch + 1}/{total_epochs} [Train]',
                          leave=False, dynamic_ncols=True)

        for (img1, img2), labels in train_pbar:
            img1, img2, labels = img1.to(device), img2.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(img1, img2)
            loss = criterion(outputs, labels)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            total_loss += loss.item()
            all_preds.append(outputs.detach().cpu())
            all_targets.append(labels.cpu())

            # Обновление прогресс-бара
            train_pbar.set_postfix({'loss': f'{loss.item():.4f}'})

        # ===== ВАЛИДАЦИЯ =====
        model.eval()
        val_loss = 0
        val_preds, val_targets = [], []

        # Прогресс-бар для валидации
        val_pbar = tqdm(test_loader, desc=f'Эпоха {epoch + 1}/{total_epochs} [Val]',
                        leave=False, dynamic_ncols=True)

        with torch.no_grad():
            for (img1, img2), labels in val_pbar:
                img1, img2, labels = img1.to(device), img2.to(device), labels.to(device)
                outputs = model(img1, img2)
                loss = criterion(outputs, labels)

                val_loss += loss.item()
                val_preds.append(outputs.cpu())
                val_targets.append(labels.cpu())

                # Обновление прогресс-бара
                val_pbar.set_postfix({'loss': f'{loss.item():.4f}'})

        # ===== ВЫЧИСЛЕНИЕ МЕТРИК =====
        # Объединение предсказаний
        all_preds = torch.cat(all_preds)
        all_targets = torch.cat(all_targets)
        val_preds = torch.cat(val_preds)
        val_targets = torch.cat(val_targets)

        # Метрики
        train_metrics = calculate_metrics(all_preds, all_targets)
        val_metrics = calculate_metrics(val_preds, val_targets)
        cm = create_confusion_matrix(val_preds, val_targets)

        # Средние потери
        avg_train_loss = total_loss / len(train_loader)
        avg_val_loss = val_loss / len(test_loader)

        # Обновление истории
        history['train_loss'].append(avg_train_loss)
        history['val_loss'].append(avg_val_loss)
        history['train_f1'].append(train_metrics['f1'])
        history['val_f1'].append(val_metrics['f1'])
        history['val_precision'].append(val_metrics['precision'])
        history['val_recall'].append(val_metrics['recall'])
        history['learning_rates'].append(optimizer.param_groups[0]['lr'])

        # Обновление scheduler
        scheduler.step()

        # ===== ЛОГИРОВАНИЕ =====
        print(f"\n================== Эпоха {epoch + 1}/{total_epochs} завершена ==================")
        print(f"Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f}")
        print(f"Train F1: {train_metrics['f1']:.4f} | Val F1: {val_metrics['f1']:.4f}")
        print(f"Val Precision: {val_metrics['precision']:.4f} | Recall: {val_metrics['recall']:.4f}")
        print(f"Learning Rate: {optimizer.param_groups[0]['lr']:.6f}")

        # ===== СОХРАНЕНИЕ ЛУЧШЕЙ МОДЕЛИ =====
        if val_metrics['f1'] > best_f1:
            best_f1 = val_metrics['f1']
            best_epoch = epoch
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'f1': best_f1,
                'metrics': val_metrics,
                'confusion_matrix': cm.tolist()
            }, best_model_path)
            print(f"Новая лучшая модель сохранена! F1: {best_f1:.4f}")

        if plot_on_train:
            # ===== ОТОБРАЖЕНИЕ ГРАФИКОВ КАЖДУЮ ЭПОХУ =====
            plot_training_history(history)
            plot_confusion_matrix(cm)

    # ===== ФИНАЛЬНОЕ СОХРАНЕНИЕ =====
    print(f"ОБУЧЕНИЕ ЗАВЕРШЕНО")
    print(f"Лучший F1-скор: {best_f1:.4f} на эпохе {best_epoch + 1}")

    # Сохранение финальной модели
    torch.save({
        'epoch': total_epochs,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'best_f1': best_f1,
        'best_epoch': best_epoch,
        'history': history
    }, final_model_path)
    return model, history


def evaluate_model(model, test_loader, device):
    # Финальная оценка качества модели
    model.eval()
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for (img1, img2), labels in tqdm(test_loader, desc="Тестирование"):
            img1, img2, labels = img1.to(device), img2.to(device), labels.to(device)
            outputs = model(img1, img2)
            all_preds.append(outputs.cpu())
            all_targets.append(labels.cpu())

    all_preds = torch.cat(all_preds)
    all_targets = torch.cat(all_targets)

    # Вычисление метрик
    metrics = calculate_metrics(all_preds, all_targets)
    cm = create_confusion_matrix(all_preds, all_targets)

    print("Финальные метрики качества:")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"F1-Score: {metrics['f1']:.4f}")
    # Визуализация
    plot_confusion_matrix(cm)
