# Daily Quiz

A Python-based web application for tracking daily quiz game scores. Create your profile and keep track of your performance across multiple popular daily quiz games!

## Features

- 🔐 User authentication (register, login, logout)
- 👤 Personal user profiles
- 📊 Score tracking for multiple games
- 📈 Statistics and analytics for each game
- 🎮 Direct links to 6 popular daily quiz games:
  - [Wordle](https://www.nytimes.com/games/wordle/index.html) - Guess the five-letter word
  - [Wørdle](https://xn--wrdle-vua.dk/) - Danish version of Wordle
  - [Worldle](https://worldle.teuteuf.fr/) - Guess the country by its shape
  - [Travle](https://travle.earth/) - Travel between countries
  - [Bandle](https://bandle.app/daily) - Guess the song
  - [Actorle](https://actorle.com/) - Guess the actor

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (SQLAlchemy)
- **Authentication**: Flask-Login
- **Frontend**: HTML, CSS, Jinja2 templates

## Installation

1. Clone the repository:
```bash
git clone https://github.com/EdvinHildestad/daily-quiz.git
cd daily-quiz
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Usage

1. **Register** for a new account
2. **Login** with your credentials
3. Browse the available daily quiz games
4. Play the games on their respective websites
5. **Add your scores** after completing each game
6. View your **statistics and history** on your profile page

## Configuration

You can configure the application using environment variables:

- `SECRET_KEY`: Secret key for session management (default: 'dev-secret-key-change-in-production')
- `DATABASE_URL`: Database connection string (default: 'sqlite:///daily_quiz.db')

Create a `.env` file in the root directory to set these variables:

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///daily_quiz.db
```

## Project Structure

```
daily-quiz/
├── app.py              # Main application file
├── models.py           # Database models
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   └── add_score.html
└── static/            # Static files
    └── css/
        └── style.css
```

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.