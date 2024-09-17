from flask import Flask, render_template, redirect, url_for, request, flash, abort, jsonify
from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped
from sqlalchemy import String
# from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
import os
import random
from webform import CafeForm, ContactForm
import time
from messages import Messages

app = Flask(__name__)
app.secret_key = os.environ.get('secret')

bootstrap = Bootstrap5(app)

message = Messages()


# Database

class Base(DeclarativeBase):
    pass


# Construct DB OB
db = SQLAlchemy(model_class=Base)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
# initialize the app with the extension
db.init_app(app)


# database table model
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    has_sockets: Mapped[bool] = mapped_column(nullable=False)
    has_toilet: Mapped[bool] = mapped_column(nullable=False)
    has_wifi: Mapped[bool] = mapped_column(nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=False)

    def covert_dict(self):
        # use Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# create Table in Cafes Database if they do not already exist
with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def home():
    year = datetime.now().year
    if request.method == 'POST':
        cafe_ = request.form.get('search_cafe')
        cafes = db.session.execute(db.select(Cafe).where(Cafe.location == cafe_)).scalars().all()

        if cafes:

            return render_template('index.html', cafe=cafes, year=year)
        else:
            flash(f"Sorry we don't have a Cafe in {cafe_}")
            time.sleep(3)
            return redirect(url_for('home'))
    else:

        cafes = db.session.execute(db.select(Cafe).order_by(Cafe.id)).scalars().all()
        return render_template('index.html', cafe=cafes, year=year)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        messages = f'Subject: {form.name.data} \n\n {form.description.data}'
        address = form.email.data
        message.send_mail(address=address, message=messages)

        flash('Message sent Successfully ')
    return render_template('contact.html', form=form)


@app.route('/cafe', methods=['GET', 'POST'])
def cafe():
    form = CafeForm()

    return render_template('add_cafe.html', form=form)


# API Section

@app.route('/random')
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)

    return jsonify(random_cafe.covert_dict())


@app.route('/all')
def get_all_cafes():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()

    return jsonify(cafes=[cafes.covert_dict() for cafes in all_cafes])


@app.route('/search/')
def search_location():
    loc = request.args.get('loc')
    location = db.session.execute(db.select(Cafe).where(Cafe.location == loc)).scalars().all()
    error_code = {
        "Not found": {"Error": "Sorry we don't have a Cafe at that location"}
    }

    if location:
        return jsonify(cafes=[cafes.covert_dict() for cafes in location])
    else:
        return jsonify(error_code)


@app.route('/add', methods=['POST'])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route('/update-price/<cafe_id>/', methods=['PATCH'])
def price_update(cafe_id):
    new_price = request.args.get('price')
    database_row = db.get_or_404(Cafe, cafe_id)

    if database_row:
        success = {
            'success': "Successfully updated price."
        }

        database_row.coffee_price = new_price
        db.session.commit()

        return jsonify(success, 200)

    else:

        error = {
            'Failed': " Sorry a cafe with that id was not found in the database."
        }

        return jsonify(error, 404)


@app.route('/report-closed/<cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    api_key = request.args.get('api-key')

    cafe_id = db.get_or_404(Cafe, cafe_id)

    if api_key == 'TopSecretAPIKey':
        if cafe_id:
            db.session.delete(cafe_id)
            db.session.commit()

            success = {

                "Success": "Successfully deleted cafe. "

            }

            return jsonify(success, 200)
        else:

            error = {
                'Failed': " Sorry a cafe with that id was not found in the database."
            }

            return jsonify(error)


    else:

        api = {
            'Key_Error': 'Sorry, that is not allowed, make sure you have the correct API-KEY '
        }

        return jsonify(api)


if __name__ == '__main__':
    app.run(debug=True)
