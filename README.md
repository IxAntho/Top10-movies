# Top 10 Movies

This is a Flask web application that allows users to create and manage a list of their top 10 favorite movies. Users can add new movies to the list, edit movie ratings and reviews, and delete movies from the list.

## Features

- Add new movies to the list by searching for them using the TMDB API
- Edit movie ratings and reviews
- Delete movies from the list
- View the list of top 10 movies in a visually appealing card format

## Prerequisites

Before running the application, make sure you have the following installed:

- Python 3.x
- Flask
- Flask-Bootstrap5
- Flask-SQLAlchemy
- Flask-WTF
- requests

You can install the required packages using the following command:
```commandline
pip install flask flask-bootstrap5 flask-sqlalchemy flask-wtf requests python-dotenv
```

## Environment Variables

This project requires an API key and API token from the TMDB (The Movie Database) API. To set up the environment variables, follow these steps:

1. Create a new file called `.env` in the project root directory.
2. Open the `.env` file and add the following lines, replacing `YOUR_API_KEY` and `YOUR_API_TOKEN` with the actual values from TMDB.

## Running the Application

1. Open a terminal or command prompt and navigate to the project directory.
2. Run the following command to start the Flask development server:
```commandline
python main.py
```
3. Open your web browser and visit `http://127.0.0.1:5000` to access the application.

## Usage

- On the home page, you'll see the list of your top 10 movies (if any have been added).
- Click the "Add Movie" button to search for a new movie using the TMDB API.
- Select the movie you want to add from the search results.
- Edit the movie's rating and review on the next page, and click "Submit" to add it to your list.
- On the home page, you can click the "Update" button to edit a movie's rating and review, or the "Delete" button to remove it from the list.

## Database

The application uses an SQLite database to store the movie data. The database file (`top-movies.db`) will be created automatically in the project directory if it doesn't exist.
