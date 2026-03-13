"""
Главный файл веб-приложения для обработки изображений
с использованием периодических функций sin/cos.
"""

from flask import Flask, render_template, request, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms import SelectField, FloatField, SubmitField, FileField, BooleanField
from wtforms.validators import DataRequired, NumberRange
from werkzeug.utils import secure_filename
import os
from datetime import datetime  # Добавляем импорт для времени
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
    image = FileField('Изображение', validators=[DataRequired()])
    function_type = SelectField('Периодическая функция',
                                choices=[('sin', 'sin(x)'), ('cos', 'cos(x)')],
                                validators=[DataRequired()])
    period = FloatField('Период (пиксели)',
                        default=50.0,
                        validators=[DataRequired(), NumberRange(min=1, max=500)])
    direction = SelectField('Аргумент функции',
                            choices=[
                                ('horizontal', 'Горизонтальная (x)'),
                                ('vertical', 'Вертикальная (y)')
                            ],
                            validators=[DataRequired()])
    add_timestamp = BooleanField('Показать время создания')  # Изменили текст
    recaptcha = RecaptchaField()
    submit = SubmitField('Обработать изображение')


@app.route('/', methods=['GET', 'POST'])
def index():
    """Главная страница приложения"""
    form = ImageForm()
    original = processed = hist_orig = hist_proc = None
    processing_time = None  # Переменная для хранения времени обработки

    if form.validate_on_submit():
        file = request.files['image']

        if file and file.filename:
            filename = secure_filename(file.filename)

            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                flash('Недопустимый формат файла', 'danger')
            else:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                original = f'uploaded/{filename}'

                processed_filename = f'processed_{filename}'
                processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)

                # Применяем функцию к изображению (без временной метки на самом изображении)
                apply_periodic_function(
                    filepath,
                    processed_path,
                    function_type=form.function_type.data,
                    period=form.period.data,
                    direction=form.direction.data,
                    add_timestamp=False  # Всегда False, т.к. метку добавляем отдельно
                )

                processed = f'uploaded/{processed_filename}'

                # Сохраняем время обработки, если галочка отмечена
                if form.add_timestamp.data:
                    processing_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                base_name = os.path.splitext(filename)[0]
                hist_orig_path = os.path.join(app.config['UPLOAD_FOLDER'], f'hist_orig_{base_name}.png')
                hist_proc_path = os.path.join(app.config['UPLOAD_FOLDER'], f'hist_proc_{base_name}.png')

                plot_histogram(filepath, hist_orig_path, 'Исходное изображение')
                plot_histogram(processed_path, hist_proc_path, 'Обработанное изображение')

                hist_orig = f'uploaded/hist_orig_{base_name}.png'
                hist_proc = f'uploaded/hist_proc_{base_name}.png'

                flash('Изображение успешно обработано', 'success')

    return render_template(
        'index.html',
        form=form,
        original=original,
        processed=processed,
        hist_orig=hist_orig,
        hist_proc=hist_proc,
        processing_time=processing_time  # Передаем время в шаблон
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)