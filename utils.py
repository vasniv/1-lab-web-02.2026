"""
Вспомогательные функции для обработки изображений
и построения гистограмм распределения цветов.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def apply_periodic_function(input_path, output_path, function_type='sin', period=50.0, direction='horizontal', add_timestamp=False):
    """
    Применяет периодическую функцию (sin/cos) к изображению.

    Алгоритм:
    1. Загружает изображение и нормализует значения пикселей в диапазон [0, 1]
    2. Создаёт маску на основе выбранной функции
    3. Умножает каждый канал изображения на маску
    4. Добавляет временную метку если нужно
    5. Сохраняет результат
    """
    img = Image.open(input_path).convert('RGB')
    img_array = np.array(img, dtype=np.float32) / 255.0
    h, w, _ = img_array.shape

    func = np.sin if function_type == 'sin' else np.cos

    if direction == 'horizontal':
        x = np.arange(w)
        arg = 2 * np.pi * x / period
        mask_1d = (func(arg) + 1) / 2
        mask = np.tile(mask_1d, (h, 1))
    else:
        y = np.arange(h)
        arg = 2 * np.pi * y / period
        mask_1d = (func(arg) + 1) / 2
        mask = np.tile(mask_1d.reshape(-1, 1), (1, w))

    for c in range(3):
        img_array[:, :, c] = img_array[:, :, c] * mask

    result = (np.clip(img_array, 0, 1) * 255).astype(np.uint8)
    result_img = Image.fromarray(result)

    if add_timestamp:
        draw = ImageDraw.Draw(result_img)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw.text((10, 10), timestamp, fill=(0, 0, 0))

    result_img.save(output_path)


def plot_histogram(image_path, output_path, title):
    """
    Строит гистограмму распределения цветов для изображения.
    Отображает распределение значений пикселей для каждого канала (R, G, B).
    """
    img = np.array(Image.open(image_path).convert('RGB'))

    r = img[:, :, 0].flatten()
    g = img[:, :, 1].flatten()
    b = img[:, :, 2].flatten()

    plt.figure(figsize=(6, 3))
    plt.hist(r, bins=64, alpha=0.6, label='R', color='red', density=True)
    plt.hist(g, bins=64, alpha=0.6, label='G', color='green', density=True)
    plt.hist(b, bins=64, alpha=0.6, label='B', color='blue', density=True)

    plt.title(title)
    plt.xlabel('Интенсивность')
    plt.ylabel('Плотность')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()