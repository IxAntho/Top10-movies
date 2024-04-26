from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, select
from sqlalchemy.exc import IntegrityError
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired
import requests
import os
from dotenv import load_dotenv
import json

# Env variables
load_dotenv(".env")
API_KEY: str = os.getenv("API_KEY")
API_TOKEN: str = os.getenv("API_TOKEN")

DB_PATH = os.path.join(os.path.dirname(__file__), "top-movies.db")

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


# CREATE DB
class Base(DeclarativeBase):
    pass


# first config specifies the path where our db is going to be created
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CREATE TABLE
class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(350), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    review: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


# Create db
with app.app_context():
    if not os.path.exists(DB_PATH):
        db.create_all()
        print("Database created.")
    else:
        print("Database already exists.")


# Edit form
class EditForm(FlaskForm):
    rating = FloatField('Your rating out of 10, e.g. 7.5', validators=[DataRequired()])
    review = StringField('Your review', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Submit')


# # Testing adding a new movie
# with app.app_context():
#     new_movie = Movie(
#         title="Phone Booth",
#         year=2002,
#         description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#         rating=7.3,
#         ranking=10,
#         review="My favourite character was the caller.",
#         img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#     )
#     db.session.add(new_movie)
#
#     try:
#         db.session.commit()
#     except IntegrityError as e:
#         print(f"Error: {str(e)}")
#         db.session.rollback()
#
# with app.app_context():
#     second_movie = Movie(
#         title="Avatar The Way of Water",
#         year=2022,
#         description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#         rating=7.3,
#         ranking=9,
#         review="I liked the water.",
#         img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
#     )
#     db.session.add(second_movie)
#
#     try:
#         db.session.commit()
#     except IntegrityError as e:
#         print(f"Error: {str(e)}")
#         db.session.rollback()


@app.route("/")
def home():
    with app.app_context():
        result = db.session.execute(db.select(Movie).order_by(Movie.ranking))
        all_movies = result.scalars().all()
    return render_template("index.html", movies=all_movies)


@app.route("/edit/<int:movie_id>", methods=["GET", "POST"])
def edit(movie_id):
    movie = db.get_or_404(Movie, movie_id)

    form = EditForm(obj=movie)
    if form.validate_on_submit():
        # Different way to update a movie entry,
        # since we previously get hold of the movie object what's left is
        # just change its attributes' values just like any other variable
        movie.rating = form.rating.data
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", form=form, movie=movie)


@app.route("/delete/<int:movie_id>")
def delete(movie_id):
    movie_to_delete = db.get_or_404(Movie, movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/find", methods=["GET", "POST"])
def find():
    add_form = AddForm()
    if add_form.validate_on_submit():
        query = add_form.title.data
        url = f"https://api.themoviedb.org/3/search/movie?query={query}&include_adult=true&language=en-US&page=1"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {API_TOKEN}"
        }

        response = requests.get(url, headers=headers)
        movies_data = response.json()["results"]

        return render_template("select.html", movies=movies_data)
    return render_template("add.html", form=add_form)


def define_ranking():
    with app.app_context():
        result = db.session.execute(db.select(Movie).order_by(Movie.rating.desc()))
        all_movies = result.scalars().all()
        # Assign unique rankings based on the ordered list
        for i, movie in enumerate(all_movies, start=1):
            movie.ranking = i
        # Commit the changes to the database
        db.session.commit()


@app.route("/add")
def add():
    movie_data = request.args.get("movie")

    if movie_data:
        # Convert the movie string to a dictionary
        movie_data = json.loads(movie_data)

        # Extract the required data from the movie dictionary
        title = movie_data.get("original_title")
        year = int(movie_data.get("release_date", "").split("-")[0]) or None
        description = movie_data.get("overview")
        rating = 0
        ranking = 0  # Set a fixed ranking for now
        review = "No review yet."  # Set a default review
        img_url = f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path')}"

        # Create a new Movie object
        new_movie = Movie(
            title=title,
            year=year,
            description=description,
            rating=rating,
            ranking=ranking,
            review=review,
            img_url=img_url
        )

        # Add the new movie to the database
        db.session.add(new_movie)

        try:
            db.session.commit()
            # Get the ID of the newly added movie
            new_movie_id = new_movie.id
            # Redirect to the edit function with the new movie ID
            define_ranking()
            return redirect(url_for("edit", movie_id=new_movie_id))
        except IntegrityError as e:
            print(f"Error: {str(e)}")
            db.session.rollback()
            return redirect(url_for("home"))
        except json.JSONDecodeError as e:
            print(f"Error: {str(e)}")
            return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
