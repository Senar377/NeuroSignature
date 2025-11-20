import pandas as pd
from torch.utils.data import Dataset, DataLoader
import os
import torch
import torchvision.transforms as transforms
from PIL import Image
from Visual_func import visualize_pair

class SignaturePairDataset(Dataset):
    def __init__(self, csv_path, img_root_dir, transform=None):
        # Читаем CSV
        self.annotations = pd.read_csv(
            csv_path,
            header=None,
            skiprows=1,  # Пропускаем первую строку (0,1,2)
            names=['img1', 'img2', 'label'],
            sep=','  # Разделитель
        )
        self.img_root_dir = img_root_dir
        self.transform = transform
        
        print(f"Количество образцов в датасете: {self.__len__()}")

    
    def __len__(self):
        return len(self.annotations)
    
    def __getitem__(self, idx):
        row = self.annotations.iloc[idx] # Получаем строку из файла по индексу

        img1_path = os.path.normpath(os.path.join(self.img_root_dir, row['img1'])) # Путь к оригинальной картинке
        img2_path = os.path.normpath(os.path.join(self.img_root_dir, row['img2'])) # Путь к проверяемой картинке

        # Значение подлнности: 1 - Настоящая 0 - Подделка 
        label = torch.tensor(row['label'], dtype=torch.float32)                    
        
        # Загружаем изображения в градациях серого
        img1 = Image.open(img1_path).convert('L')
        img2 = Image.open(img2_path).convert('L')
        
        # Применяем трансформации
        if self.transform:
            img1 = self.transform(img1)
            img2 = self.transform(img2)
        
        return (img1, img2), label
    

class Data_Transform:
    def __init__(self, Train_data_path, Test_data_path, Images_path, image_size = (128, 256)):
        self.cuda_available = True if torch.cuda.is_available() else False
        print("CUDA in dataloaders:", self.cuda_available,"\n")

        self.Train_data_path = Train_data_path
        self.Images_path = Images_path
        self.Test_data_path = Test_data_path

        self.train_dataset, self.test_dataset = None, None
        self.train_loader, self.test_loader = None, None


        # Преобразования
        self.train_transform = transforms.Compose([
            transforms.Resize(image_size),
            transforms.RandomAffine(
                degrees=3, 
                translate=(0.03, 0.03),
                scale=(0.90, 1.05),
                shear=1
            ),
            transforms.RandomPerspective(distortion_scale=0.2, p=0.3),
            transforms.RandomApply([
                transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
            ], p=0.2),

            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])

        self.test_transform = transforms.Compose([
            transforms.Resize(image_size),

            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])

    def create_datasets(self, vizual_id = 0):
        # Создание датасетов
        self.train_dataset = SignaturePairDataset(
            csv_path = self.Train_data_path,
            img_root_dir = self.Images_path,
            transform = self.train_transform
        )
        
        self.test_dataset = SignaturePairDataset(
            csv_path = self.Test_data_path,
            img_root_dir = self.Images_path,
            transform = self.test_transform
        )
        
        print(f"\nУспешно загружены датасеты:")
        print(f"Train samples: {len(self.train_dataset)}")
        print(f"Test samples: {len(self.test_dataset)}")
        
        # Визуализация примера
        print("\nВизуализация примера из датасета TRAIN")
        visualize_pair(self.train_dataset, vizual_id)
        print("Визуализация примера из датасета TEST")
        visualize_pair(self.test_dataset, vizual_id)

        return self.train_dataset, self.test_dataset
    
    def create_dataloaders(self, BATCH_SIZE = 32, BATCH_SIZE_VAL = 32):
        self.train_loader = DataLoader(
            self.train_dataset,
            batch_size=BATCH_SIZE,
            shuffle=True,
            pin_memory=self.cuda_available
        )

        self.test_loader = DataLoader(
            self.test_dataset,
            batch_size=BATCH_SIZE_VAL,
            shuffle=False,
            pin_memory=self.cuda_available
        )

        print(f"DataLoaders:")
        print(f"Train batches: {len(self.train_loader)}")
        print(f"Test batches: {len(self.test_loader)}")
        
        return self.train_loader, self.test_loader
