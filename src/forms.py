from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class UploadForm(FlaskForm):
    file1 = FileField(
        label='Загрузите файл',
        validators=[FileField(message='Обязательное поле')]
    )
    file2 = FileField(
        label='Загрузите файл',
        validators=[FileField(message='Обязательное поле')]
    )
    submit = SubmitField('Отправить')
    