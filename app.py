from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from models import db, User, Score
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Quiz games configuration
QUIZ_GAMES = [
    {
        'name': 'Wordle',
        'url': 'https://www.nytimes.com/games/wordle/index.html',
        'description': 'Guess the five-letter word in six tries'
    },
    {
        'name': 'Wørdle',
        'url': 'https://xn--wrdle-vua.dk/',
        'description': 'Danish version of Wordle'
    },
    {
        'name': 'Worldle',
        'url': 'https://worldle.teuteuf.fr/',
        'description': 'Guess the country by its shape'
    },
    {
        'name': 'Travle',
        'url': 'https://travle.earth/',
        'description': 'Travel between countries in the fewest steps'
    },
    {
        'name': 'Bandle',
        'url': 'https://bandle.app/daily',
        'description': 'Guess the song from progressively longer clips'
    },
    {
        'name': 'Actorle',
        'url': 'https://actorle.com/',
        'description': 'Guess the actor from their movies'
    }
]

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


@app.route('/')
def index():
    """Homepage with quiz game links."""
    return render_template('index.html', games=QUIZ_GAMES)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        #email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate input
        if not username or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')
        
        login_user(user, remember=remember)
        
        # Redirect to next page or index
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        
        return redirect(next_page)
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    """User profile page showing scores."""
    # Get all scores for current user
    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.date.desc()).all()
    
    # Calculate statistics
    game_stats = {}
    for game in QUIZ_GAMES:
        game_name = game['name']
        game_scores = [s for s in scores if s.game_name == game_name]
        if game_scores:
            total = sum(s.tries for s in game_scores)  # Use `tries` instead of `score`
            avg = total / len(game_scores)
            best = min(s.tries for s in game_scores)  # Least tries is the best
            game_stats[game_name] = {
                'total': total,
                'average': round(avg, 2),
                'best': best,
                'count': len(game_scores)
            }
        else:
            game_stats[game_name] = None
    
    return render_template('profile.html', scores=scores, game_stats=game_stats, games=QUIZ_GAMES)


@app.route('/add_score/<game_name>', methods=['GET', 'POST'])
@login_required
def add_score(game_name):
    """Add or update the least number of tries for a specific game and date."""
    # Validate game name
    valid_games = [game['name'] for game in QUIZ_GAMES]
    if game_name not in valid_games:
        flash('Invalid game name.', 'danger')
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        tries = request.form.get('tries')
        date_str = request.form.get('date')
        
        try:
            tries = int(tries)
            if date_str:
                score_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                score_date = datetime.utcnow().date()
            
            # Check if a score already exists for this game and date
            existing_score = Score.query.filter_by(
                user_id=current_user.id,
                game_name=game_name,
                date=score_date
            ).first()
            
            if existing_score:
                # Update the score only if the new number of tries is less
                if tries < existing_score.tries:
                    existing_score.tries = tries
                    existing_score.created_at = datetime.utcnow()
                    flash(f'New best score for {game_name} on {score_date}!', 'success')
                else:
                    flash(f'Your current best score for {game_name} on {score_date} remains {existing_score.tries} tries.', 'info')
            else:
                # Create a new score
                score = Score(
                    user_id=current_user.id,
                    game_name=game_name,
                    tries=tries,
                    date=score_date
                )
                db.session.add(score)
                flash(f'Score for {game_name} added!', 'success')
            
            db.session.commit()
            return redirect(url_for('profile'))
            
        except ValueError:
            flash('Invalid number of tries or date format.', 'danger')
    
    # Get today's date for the form default
    today = datetime.utcnow().date().strftime('%Y-%m-%d')
    return render_template('add_score.html', game_name=game_name, today=today)
    """Add or update the least number of tries for a specific game and date."""
    # Validate game name
    valid_games = [game['name'] for game in QUIZ_GAMES]
    if game_name not in valid_games:
        flash('Invalid game name.', 'danger')
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        tries = request.form.get('tries')
        date_str = request.form.get('date')
        
        try:
            tries = int(tries)
            if date_str:
                score_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                score_date = datetime.utcnow().date()
            
            # Check if a score already exists for this game and date
            existing_score = Score.query.filter_by(
                user_id=current_user.id,
                game_name=game_name,
                date=score_date
            ).first()
            
            if existing_score:
                # Update the score only if the new number of tries is less
                if tries < existing_score.tries:
                    existing_score.tries = tries
                    existing_score.created_at = datetime.utcnow()
                    flash(f'New best score for {game_name} on {score_date}!', 'success')
                else:
                    flash(f'Your current best score for {game_name} on {score_date} remains {existing_score.tries} tries.', 'info')
            else:
                # Create a new score
                score = Score(
                    user_id=current_user.id,
                    game_name=game_name,
                    tries=tries,
                    date=score_date
                )
                db.session.add(score)
                flash(f'Score for {game_name} added!', 'success')
            
            db.session.commit()
            return redirect(url_for('profile'))
            
        except ValueError:
            flash('Invalid number of tries or date format.', 'danger')
    
    # Get today's date for the form default
    today = datetime.utcnow().date().strftime('%Y-%m-%d')
    return render_template('add_score.html', game_name=game_name, today=today)

@app.route('/delete_score/<int:score_id>', methods=['POST'])
@login_required
def delete_score(score_id):
    """Delete a score."""
    score = Score.query.get_or_404(score_id)
    
    # Ensure user owns this score
    if score.user_id != current_user.id:
        flash('You cannot delete this score.', 'danger')
        return redirect(url_for('profile'))
    
    db.session.delete(score)
    db.session.commit()
    flash('Score deleted.', 'info')
    return redirect(url_for('profile'))

@app.route('/scores')
def scores():
    """Display the least number of tries per day, per game for all users."""
    # Query all scores grouped by user, game, and date
    scores = db.session.query(
        User.username,
        Score.game_name,
        Score.date,
        db.func.min(Score.tries).label('least_tries')
    ).join(User).group_by(User.username, Score.game_name, Score.date).all()

    # Render the scores page
    return render_template('scores.html', scores=scores)

def create_tables():
    """Create database tables."""
    with app.app_context():
        db.create_all()


if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
