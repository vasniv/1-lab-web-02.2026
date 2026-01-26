from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from werkzeug.utils import secure_filename
import os

# Утилиты для обработки изображений
from utils import apply_periodic_function, plot_histograms

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-123')
app.config['UPLOAD_FOLDER'] = 'static/uploaded'

# Инициализируем Bootstrap
Bootstrap(app)

# Создаем папку если ее нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Максимальный размер файла 5MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


# Простая форма для параметров
class ImageForm(FlaskForm):
    function_type = SelectField('Функция',
                                choices=[('sin', 'Синус (sin)'), ('cos', 'Косинус (cos)')],
                                validators=[DataRequired()])
    period = FloatField('Период (пиксели)',
                        default=50.0,
                        validators=[DataRequired(), NumberRange(min=1, max=1000)])
    direction = SelectField('Направление аргумента',
                            choices=[('horizontal', 'Горизонтальное (x)'), ('vertical', 'Вертикальное (y)')],
                            validators=[DataRequired()])
    submit = SubmitField('Обработать изображение')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ImageForm()
    original = processed = hist_orig = hist_proc = None

    if form.validate_on_submit():
        # Проверяем наличие файла
        if 'image' not in request.files:
            return render_template('index.html', form=form, error='Файл не выбран')

        file = request.files['image']
        if file.filename == '':
            return render_template('index.html', form=form, error='Файл не выбран')

        if file:
            try:
                # Сохраняем исходное изображение
                filename = secure_filename(file.filename)
                if not filename:
                    return render_template('index.html', form=form, error='Недопустимое имя файла')

                base_name, ext = os.path.splitext(filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                original = f'uploaded/{filename}'

                # Создаем уникальные имена для обработанных файлов
                import time
                timestamp = int(time.time())
                processed_filename = f'processed_{base_name}_{timestamp}{ext}'
                processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)

                hist_orig_filename = f'hist_orig_{base_name}_{timestamp}.png'
                hist_proc_filename = f'hist_proc_{base_name}_{timestamp}.png'

                hist_orig_path = os.path.join(app.config['UPLOAD_FOLDER'], hist_orig_filename)
                hist_proc_path = os.path.join(app.config['UPLOAD_FOLDER'], hist_proc_filename)

                # Применяем периодическую функцию
                apply_periodic_function(
                    filepath,
                    processed_path,
                    function_type=form.function_type.data,
                    period=form.period.data,
                    direction=form.direction.data
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
                # Удаляем временные файлы если есть ошибка
                if 'filepath' in locals() and os.path.exists(filepath):
                    os.remove(filepath)
                return render_template('index.html', form=form, error=f'Ошибка обработки: {str(e)}')

    return render_template(
        'index.html',
        form=form,
        original=original,
        processed=processed,
        hist_orig=hist_orig,
        hist_proc=hist_proc
    )

# Точка входа при запуске напрямую
if __name__ == '__main__':
    # Получаем порт из переменной окружения
    port = int(os.environ.get('PORT', 5000))
    # Запускаем сервер: host='0.0.0.0' — чтобы приложение было доступно извне
    app.run(host='0.0.0.0', port=port, debug=False)
