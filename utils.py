"""
Вспомогательные функции для обработки изображений
и построения гистограмм распределения цветов.
"""

import numpy as np
from PIL import Image
import matplotlib

matplotlib.use('Agg')  # Использование бэкенда без графического интерфейса
import matplotlib.pyplot as plt


def apply_periodic_function(input_path, output_path, function_type='sin', period=50.0, direction='horizontal'):
    """
    Применяет периодическую функцию (sin/cos) к изображению.

    Алгоритм:
    1. Загружает изображение и нормализует значения пикселей в диапазон [0, 1]
    2. Создаёт маску на основе выбранной функции
    3. Умножает каждый канал изображения на маску
    4. Сохраняет результат

    Формула: I_new = I_original * (f(2π * coord / period) + 1) / 2
    где f - sin или cos, coord - x или y в зависимости от направления.
    """
    # Загрузка и нормализация изображения
    img = Image.open(input_path).convert('RGB')
    img_array = np.array(img, dtype=np.float32) / 255.0
    h, w, _ = img_array.shape

    # Выбор периодической функции
    func = np.sin if function_type == 'sin' else np.cos

    # Создание маски в зависимости от направления
    if direction == 'horizontal':
        # Горизонтальное направление: функция зависит от координаты x
        x = np.arange(w)
        arg = 2 * np.pi * x / period
        mask_1d = (func(arg) + 1) / 2  # Нормировка из [-1, 1] в [0, 1]
        mask = np.tile(mask_1d, (h, 1))  # Расширение маски на всю высоту
    else:  # vertical
        # Вертикальное направление: функция зависит от координаты y
        y = np.arange(h)
        arg = 2 * np.pi * y / period
        mask_1d = (func(arg) + 1) / 2
        mask = np.tile(mask_1d.reshape(-1, 1), (1, w))  # Расширение маски на всю ширину

    # Применение маски к каждому цветовому каналу
    for c in range(3):
        img_array[:, :, c] = img_array[:, :, c] * mask

    # Денормализация и сохранение результата
    result = (np.clip(img_array, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(result).save(output_path)


def plot_histogram(image_path, output_path, title):
    """
    Строит гистограмму распределения цветов для изображения.

    Отображает распределение значений пикселей
    для каждого цветового канала (R, G, B).
    """
    # Загрузка изображения
    img = np.array(Image.open(image_path).convert('RGB'))

    # Извлечение значений каждого канала
    r = img[:, :, 0].flatten()
    g = img[:, :, 1].flatten()
    b = img[:, :, 2].flatten()

    # Создание графика
    plt.figure(figsize=(6, 3))

    # Построение гистограмм для каждого канала с разными цветами
    plt.hist(r, bins=64, alpha=0.6, label='R', color='red', density=True)
    plt.hist(g, bins=64, alpha=0.6, label='G', color='green', density=True)
    plt.hist(b, bins=64, alpha=0.6, label='B', color='blue', density=True)

    # Настройка графика
    plt.title(title)
    plt.xlabel('Интенсивность')
    plt.ylabel('Плотность')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    # Сохранение гистограммы
    plt.savefig(output_path, dpi=100)
    plt.close()