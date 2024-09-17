from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, EmailField, IntegerField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email


class CafeForm(FlaskForm):
    Name = StringField(label='Name', validators=[DataRequired(), Length(min=2, max=50)])
    Map_url = StringField(label='Map_URL', validators=[DataRequired(), Length(max=1000)])
    Image_url = StringField(label='Image_URL', validators=[DataRequired(), Length(max=1000)])
    Location = StringField(label='Location', validators=[DataRequired()])
    Seats = IntegerField(label='Seats', validators=[DataRequired()])
    Coffee_Price = StringField(label='Coffee_price', validators=[DataRequired()])
    Has_toilet = BooleanField()
    Has_wifi = BooleanField()
    Has_sockets = BooleanField()
    Can_take_calls = BooleanField()
    Submit = SubmitField(label='Add Cafe')


class ContactForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = EmailField(label='Email', validators=[DataRequired()])
    description = TextAreaField(label='Description', validators=[DataRequired()])
    submit = SubmitField(label='Submit')


