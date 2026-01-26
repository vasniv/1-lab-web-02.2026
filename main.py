"""
Главный файл веб-приложения для обработки изображений
с использованием периодических функций sin/cos.

Функционал:
- Загрузка изображения
- Применение периодической функции (sin/cos)
- Построение гистограмм распределения цветов
- Проверка на робота (reCAPTCHA)
"""

from flask import Flask, render_template, request, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms import SelectField, FloatField, SubmitField, FileField
from wtforms.validators import DataRequired, NumberRange
from werkzeug.utils import secure_filename
import os
from utils import apply_periodic_function, plot_histogram

# Инициализация приложения Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
app.config['UPLOAD_FOLDER'] = 'static/uploaded'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LeI51YsAAAAAAz0ODUfObX7-rWcPSxAj_MvQAD6'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LeI51YsAAAAAGk_94oM9JX4BtpDNltzq3P6zy1B'

Bootstrap(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


class ImageForm(FlaskForm):
    """Форма для загрузки и обработки изображения"""

    # Поле загрузки файла изображения
    image = FileField('Изображение', validators=[DataRequired()])

    # Выбор периодической функции (sin или cos)
    function_type = SelectField('Периодическая функция',
                                choices=[('sin', 'sin(x)'), ('cos', 'cos(x)')],
                                validators=[DataRequired()])

    # Период функции в пикселях
    period = FloatField('Период (пиксели)',
                        default=50.0,
                        validators=[DataRequired(), NumberRange(min=1, max=500)])

    # Направление применения функции (горизонтальное/вертикальное)
    direction = SelectField('Аргумент функции',
                            choices=[
                                ('horizontal', 'Горизонтальная (x)'),
                                ('vertical', 'Вертикальная (y)')
                            ],
                            validators=[DataRequired()])

    # reCAPTCHA для проверки на робота
    recaptcha = RecaptchaField()

    # Кнопка отправки формы
    submit = SubmitField('Обработать изображение')


@app.route('/', methods=['GET', 'POST'])
def index():
    """Главная страница приложения"""
    form = ImageForm()
    original = processed = hist_orig = hist_proc = None

    # Обработка отправленной формы
    if form.validate_on_submit():
        file = request.files['image']

        if file and file.filename:
            # Безопасное имя файла
            filename = secure_filename(file.filename)

            # Проверка формата файла
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                flash('Недопустимый формат файла', 'danger')
            else:
                # Сохранение загруженного файла
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                original = f'uploaded/{filename}'

                # Обработка изображения
                processed_filename = f'processed_{filename}'
                processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)

                apply_periodic_function(
                    filepath,
                    processed_path,
                    function_type=form.function_type.data,
                    period=form.period.data,
                    direction=form.direction.data
                )

                processed = f'uploaded/{processed_filename}'

                # Построение гистограмм распределения цветов
                base_name = os.path.splitext(filename)[0]
                hist_orig_path = os.path.join(app.config['UPLOAD_FOLDER'], f'hist_orig_{base_name}.png')
                hist_proc_path = os.path.join(app.config['UPLOAD_FOLDER'], f'hist_proc_{base_name}.png')

                plot_histogram(filepath, hist_orig_path, 'Исходное изображение')
                plot_histogram(processed_path, hist_proc_path, 'Обработанное изображение')

                hist_orig = f'uploaded/hist_orig_{base_name}.png'
                hist_proc = f'uploaded/hist_proc_{base_name}.png'

                flash('Изображение успешно обработано', 'success')

    # Отображение страницы с результатами
    return render_template(
        'index.html',
        form=form,
        original=original,
        processed=processed,
        hist_orig=hist_orig,
        hist_proc=hist_proc
    )


if __name__ == '__main__':
    # Запуск приложения в режиме отладки
    app.run(debug=True, host='0.0.0.0', port=5000)