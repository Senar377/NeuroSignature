

import tensorflow as tf 
from tensorflow.keras.models import Sequential     # noqa
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout 
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split 
import numpy as np 
import os
import sys
import cv2

from tensorflow.keras.models import load_model                                      #убирать коммент, когда не нужно переобучать + закомм обучение внизу
model = load_model("signature_verification_model.keras")    #

# === Шаг 1: Загрузка и подготовка данных === 
original_signatures_path = "D:/KAFEDRA/neuro/original" 
forged_signatures_path = "D:/KAFEDRA/neuro/forged"

def load_images(image_dir):
    images = [] 
    labels = []
    for file_name in os.listdir(image_dir): 
        file_path = os.path.join(image_dir, file_name) 
        
        # Загружаем изображения в цвете 
        img = tf.keras.preprocessing.image.load_img(
            file_path, target_size=(128, 128), color_mode="grayscale") 
        img_array = tf.keras.preprocessing.image.img_to_array(img) / 255.0 
        
        # Нормализация 
        images.append(img_array) 
        
        # Метка (1 для оригинала, 0 для подделки) 
        labels.append(1 if "original" in image_dir else 0) 
    return np.array(images), np.array(labels)

original_images, original_labels = load_images(original_signatures_path) 
forged_images, forged_labels = load_images(forged_signatures_path) 

# Объединение данных
all_images = np.concatenate([original_images, forged_images], axis=0) 
all_labels = np.concatenate([original_labels, forged_labels], axis=0)




# Разделение данных на тренировочные и тестовые 
X_train, X_test, y_train, y_test = train_test_split(all_images, 
                    all_labels, test_size=0.3, random_state=42)
#место отключение обучения
# === Шаг 2: Создание модели === 
model = Sequential([ 
                    Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 1)), 
                    MaxPooling2D((2, 2)), 
                    Conv2D(64, (3, 3), activation='relu'), 
                    MaxPooling2D((2, 2)), 
                    Conv2D(128, (3, 3), activation='relu'), 
                    MaxPooling2D((2, 2)), 
                    Flatten(), 
                    Dense(128, activation='relu'), 
                    Dropout(0.5), 
                    Dense(1, activation='sigmoid') # Выходной слой для бинарной классификации 
                    ])

# Компиляция модели 
model.compile(optimizer='adam', 
              loss='binary_crossentropy', 
              metrics=['accuracy'])

# === Шаг 3: Аугментация данных === 
data_generator = ImageDataGenerator( 
    rotation_range=10, 
    width_shift_range=0.1, 
    height_shift_range=0.1, 
    shear_range=0.1, 
    zoom_range=0.1, 
    horizontal_flip=True, 
    vertical_flip=True # Дополнительная аугментация с вертикальным отражением  !!!!(было True)!!!!
    )



# === Шаг 4: Обучение модели === 
history = model.fit( 
    data_generator.flow(X_train, y_train, batch_size=32), 
    validation_data=(X_test, y_test), 
    epochs=30
    )



# === Шаг 5: Оценка модели === 
test_loss, test_accuracy = model.evaluate(X_test, y_test) 
print(f"Точность на тестовых данных: {test_accuracy * 100:.2f}%")
print(f"Потери на тестовых данных: {test_loss * 100:.2f}%")

# === Шаг 6: Сохранение модели === 
model.save("signature_verification_model.keras") #до этого было signature_verification_model.h5

#'''
# === Шаг 7: Инференс (предсказание) === 



def analyze_writing_speed(image):
    """
    Анализ скорости написания подписи по одному статичному изображению.
    Проводится через анализ контуров штрихов:
    - Меньше контура и длиннее - быстрее почерк.
    - Больше мелких контуров - медленнее и осторожнее.
    #место отключение обучения
    """
    
    # Преобразуем изображение в оттенки серого, если необходимо
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Применим пороговую бинаризацию (инвертированную, чтобы линии были белые)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    # Находим контуры
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if not contours:
        return "недостаточно данных"

    # Вычисляем длину каждого контура (периметр)
    contour_lengths = [cv2.arcLength(cnt, False) for cnt in contours]

    # Средняя длина контура
    avg_length = np.mean(contour_lengths)
    # Количество контуров
    count = len(contours)

    # Логика определения скорости по порогам (эти значения можно настраивать)
    if count < 30 and avg_length > 150:
        return "быстрая"
    elif count > 70 and avg_length < 80:
        return "медленная"
    else:
        return "обдуманная"

def analyze_movement_coordination(image):
    # Преобразуем изображение в оттенки серого, если необходимо
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Применим пороговую бинаризацию (инвертированную, чтобы линии были белые)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    # Находим контуры
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if not contours:
        return "недостаточно данных"
    # Количество контуров
    count = len(contours)
    return count

def analyze_fluctuations(image):
    """
    Анализ колебаний и кривизны линий в подписи.
    Использует контуры для определения углов между сегментами линий.
    """

    # Преобразуем изображение в оттенки серого
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    # Применяем пороговую бинаризацию
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # Находим контуры
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return "недостаточно данных"
    
    # Список для хранения углов
    angles = []
    
    for cnt in contours:
        # Упрощаем контур для уменьшения количества точек
        epsilon = 0.01 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        # Вычисляем углы между сегментами
        for i in range(len(approx)):
            p1 = approx[i][0]
            p2 = approx[(i + 1) % len(approx)][0]
            p3 = approx[(i + 2) % len(approx)][0]
            # Векторы
            v1 = p2 - p1
            v2 = p3 - p2
            # Вычисляем угол между векторами
            angle = np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])
            angle = np.abs(angle) * (180 / np.pi)  # Преобразуем в градусы
            # Добавляем угол в список
            angles.append(angle)
            
    # Оценка колебаний на основе средней кривизны
    avg_angle = np.mean(angles)
    # Логика определения уровня колебаний по порогам
    if avg_angle < 10:
        return "нормальные"
    elif avg_angle < 30:
        return "высокие"
    else:
        return "низкие"

def analyze_letter_shapes(image):
    """
    Анализ сложности форм букв в подписи.
    Использует контуры для определения количества вершин и длины.
    """
    # Преобразуем изображение в оттенки серого
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    # Применяем пороговую бинаризацию
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # Находим контуры
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return "недостаточно данных"
    # Списки для хранения характеристик контуров
    num_vertices = []
    lengths = []
    
    for cnt in contours:
        # Упрощаем контур для уменьшения количества точек
        epsilon = 0.01 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        # Сохраняем количество вершин и длину контура
        num_vertices.append(len(approx))
        lengths.append(cv2.arcLength(cnt, True))
    # Оценка сложности форм на основе характеристик
    avg_vertices = np.mean(num_vertices)
    avg_length = np.mean(lengths)
    # Логика определения сложности форм по порогам
    if avg_vertices > 8 and avg_length > 100:
        return "сложные"
    elif avg_vertices < 5 and avg_length < 50:
        return "упрощенные"
    else:
        return "умеренные"

def extract_features(image_path):
    # Загрузка изображения
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (128, 128))  # Изменение размера для согласования с моделью
    # Анализ различных характеристик
    speed = analyze_writing_speed(img)
    coordination = analyze_movement_coordination(img)
    fluctuations = analyze_fluctuations(img)
    letter_shapes = analyze_letter_shapes(img)
    return {
        "Скорость:": speed,
        "Количество контуров:": coordination,
        "Анализ колебаний и кривизны линий в подписи:": fluctuations,
        "Формы букв:": letter_shapes
    }


# Пример использования
features = extract_features("D:/KAFEDRA/neuro/exp/Olia.jpg")
#print(features)




def predict_signature_with_analysis(image_path):
    # Анализ почерка
    features = extract_features(image_path)
    
    # Предсказание с использованием модели
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=(128, 128), color_mode="grayscale") 
    img_array = tf.keras.preprocessing.image.img_to_array(img) / 255.0 
    img_array = np.expand_dims(img_array, axis=0)  # Добавление batch dimension 
    prediction = model.predict(img_array)
    confidence = prediction[0][0] * 100
    print()
    # Вывод результатов
    if confidence > 81:
        print(f"Оригинал. Схожесть: {confidence:.2f}%")
    else:
        print(f"Подделка. Схожесть: {confidence:.2f}%")
    
    # Вывод характеристик почерка
    print()
    print("===Анализ почерка===")
    print()
    for key, value in features.items():
        print(key, value)
# Пример использования
predict_signature_with_analysis("D:/KAFEDRA/neuro/exp/Olia.jpg")