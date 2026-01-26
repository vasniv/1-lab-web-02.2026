import numpy as np
from PIL import Image
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


def apply_periodic_function(input_path, output_path, function_type='sin',
                            period=50.0, direction='horizontal'):
    """
    Умножает изображение на периодическую функцию sin или cos с нормировкой.

    Аргумент функции определяется:
    - 'horizontal': аргумент = горизонтальная координата (x)
    - 'vertical': аргумент = вертикальная координата (y)
    """
    # Открываем и нормализуем изображение
    img = Image.open(input_path).convert('RGB')
    img_array = np.array(img, dtype=np.float32) / 255.0

    h, w, _ = img_array.shape

    # Выбираем функцию
    if function_type == 'sin':
        func = np.sin
    else:  # 'cos'
        func = np.cos

    # Создаем маску в зависимости от направления
    if direction == 'horizontal':
        # Аргумент зависит от x (горизонтальная составляющая)
        x = np.arange(w)
        # Нормированная периодическая функция: (sin(2πx/period) + 1) / 2
        # Дает значения от 0 до 1
        arg = 2 * np.pi * x / period
        mask_1d = (func(arg) + 1) / 2  # Нормировка к [0, 1]
        # Превращаем в 2D маску (одинаковая для всех строк)
        mask = np.tile(mask_1d, (h, 1))

    else:  # 'vertical'
        # Аргумент зависит от y (вертикальная составляющая)
        y = np.arange(h)
        arg = 2 * np.pi * y / period
        mask_1d = (func(arg) + 1) / 2
        # Превращаем в 2D маску (одинаковая для всех столбцов)
        mask = np.tile(mask_1d.reshape(-1, 1), (1, w))

    # Умножаем каждый цветовой канал на маску
    for c in range(3):  # R, G, B каналы
        img_array[:, :, c] = img_array[:, :, c] * mask

    # Возвращаем к диапазону 0-255 и сохраняем
    result_array = (np.clip(img_array, 0, 1) * 255).astype(np.uint8)
    result_img = Image.fromarray(result_array)
    result_img.save(output_path)


def plot_histograms(orig_path, proc_path, hist_orig_path, hist_proc_path):
    """
    Рисует графики распределения цветов для исходного и нового изображений.
    """

    def get_channel_data(img_path):
        """Извлекает данные по каналам R, G, B."""
        img = np.array(Image.open(img_path).convert('RGB'))
        r = img[:, :, 0].flatten()
        g = img[:, :, 1].flatten()
        b = img[:, :, 2].flatten()
        return r, g, b

    # Гистограмма для исходного изображения
    plt.figure(figsize=(10, 4))

    r, g, b = get_channel_data(orig_path)
    plt.subplot(1, 2, 1)
    plt.hist(r, bins=50, color='red', alpha=0.7, label='R', density=True)
    plt.hist(g, bins=50, color='green', alpha=0.7, label='G', density=True)
    plt.hist(b, bins=50, color='blue', alpha=0.7, label='B', density=True)
    plt.title('Исходное изображение')
    plt.xlabel('Интенсивность')
    plt.ylabel('Частота')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Гистограмма для обработанного изображения
    r, g, b = get_channel_data(proc_path)
    plt.subplot(1, 2, 2)
    plt.hist(r, bins=50, color='red', alpha=0.7, label='R', density=True)
    plt.hist(g, bins=50, color='green', alpha=0.7, label='G', density=True)
    plt.hist(b, bins=50, color='blue', alpha=0.7, label='B', density=True)
    plt.title('Обработанное изображение')
    plt.xlabel('Интенсивность')
    plt.ylabel('Частота')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(hist_orig_path, dpi=100)
    plt.close()

    # Простая гистограмма для сравнения
    plt.figure(figsize=(8, 4))

    r_orig, g_orig, b_orig = get_channel_data(orig_path)
    r_proc, g_proc, b_proc = get_channel_data(proc_path)

    # Объединяем все каналы для общего сравнения
    all_orig = np.concatenate([r_orig, g_orig, b_orig])
    all_proc = np.concatenate([r_proc, g_proc, b_proc])

    plt.hist(all_orig, bins=50, color='blue', alpha=0.5, label='Исходное', density=True)
    plt.hist(all_proc, bins=50, color='red', alpha=0.5, label='Обработанное', density=True)
    plt.title('Сравнение распределений цветов')
    plt.xlabel('Интенсивность')
    plt.ylabel('Частота')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(hist_proc_path, dpi=100)
    plt.close()