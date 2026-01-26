from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from utils import apply_periodic_function, plot_histograms

app = Flask(__name__)
app.config['SECRET_KEY'] = 'simple-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/uploaded'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    original = processed = hist_orig = hist_proc = None

    if request.method == 'POST':
        # Проверяем наличие файла
        if 'image' not in request.files:
            return render_template('index.html', error='Файл не выбран')

        file = request.files['image']
        if file.filename == '':
            return render_template('index.html', error='Файл не выбран')

        if file:
            # Сохраняем исходное изображение
            filename = secure_filename(file.filename)
            base_name, ext = os.path.splitext(filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            original = f'uploaded/{filename}'

            # Получаем параметры из формы
            function_type = request.form.get('function_type', 'sin')
            period = float(request.form.get('period', 50))
            direction = request.form.get('direction', 'horizontal')

            # Создаем уникальные имена для обработанных файлов
            processed_filename = f'processed_{filename}'
            processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)

            hist_orig_filename = f'hist_orig_{base_name}.png'
            hist_proc_filename = f'hist_proc_{base_name}.png'

            hist_orig_path = os.path.join(app.config['UPLOAD_FOLDER'], hist_orig_filename)
            hist_proc_path = os.path.join(app.config['UPLOAD_FOLDER'], hist_proc_filename)

            try:
                # Применяем периодическую функцию
                apply_periodic_function(
                    filepath,
                    processed_path,
                    function_type=function_type,
                    period=period,
                    direction=direction
                )

                processed = f'uploaded/{processed_filename}'

                # Создаем гистограммы
                plot_histograms(
                    filepath,
                    processed_path,
                    hist_orig_path,
                    hist_proc_path
                )

                hist_orig = f'uploaded/{hist_orig_filename}'
                hist_proc = f'uploaded/{hist_proc_filename}'

            except Exception as e:
                return render_template('index.html', error=f'Ошибка обработки: {str(e)}')

    return render_template(
        'index.html',
        original=original,
        processed=processed,
        hist_orig=hist_orig,
        hist_proc=hist_proc
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)