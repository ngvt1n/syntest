from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, Participant, Researcher, Test, TestResult, ScreeningResponse

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///synesthesia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)


# Create tables and sample data
with app.app_context():
    db.create_all()
    
    # Create sample tests if they don't exist
    if Test.query.count() == 0:
        tests = [
            Test(
                name='Trigger-Color Synesthesia Test',
                description='Test for color associations with letters, numbers, or sounds',
                synesthesia_type='trigger-color',
                duration=20
            ),
            Test(
                name='Trigger-Gustatory Synesthesia Test',
                description='Test for taste associations with various triggers',
                synesthesia_type='trigger-gustatory',
                duration=15
            ),
            Test(
                name='Sequence-Space Synesthesia Test',
                description='Test for spatial visualization of sequences',
                synesthesia_type='sequence-space',
                duration=25
            )
        ]
        db.session.add_all(tests)
        db.session.commit()


# Landing Page
@app.route('/')
def index():
    return render_template('index.html')


# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        user = None
        if role == 'participant':
            user = Participant.query.filter_by(email=email).first()
        else:
            user = Researcher.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Set session
            session['user_id'] = user.id
            session['user_role'] = role
            session['user_name'] = user.name
            
            flash('Login successful!', 'success')
            
            if role == 'participant':
                return redirect(url_for('participant_dashboard'))
            else:
                return redirect(url_for('researcher_dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        
        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html', error='Passwords do not match')
        
        # Check if user already exists
        if role == 'participant':
            existing_user = Participant.query.filter_by(email=email).first()
        else:
            existing_user = Researcher.query.filter_by(email=email).first()
        
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('signup.html', error='Email already registered')
        
        # Create new user
        password_hash = generate_password_hash(password)
        
        try:
            if role == 'participant':
                age = request.form.get('age')
                country = request.form.get('country', 'Spain')
                
                new_user = Participant(
                    name=name,
                    email=email,
                    password_hash=password_hash,
                    age=age,
                    country=country
                )
            else:
                institution = request.form.get('institution')
                access_code = request.form.get('access_code')
                
                # Validate access code
                if access_code != 'RESEARCH2025':
                    flash('Invalid researcher access code', 'error')
                    return render_template('signup.html', error='Invalid access code')
                
                new_user = Researcher(
                    name=name,
                    email=email,
                    password_hash=password_hash,
                    institution=institution
                )
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'error')
            return render_template('signup.html', error='Error creating account')
    
    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


# Participant Routes
@app.route('/participant/dashboard')
def participant_dashboard():
    if 'user_id' not in session or session.get('user_role') != 'participant':
        flash('Please login to access this page', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = Participant.query.get(user_id)
    
    # Get test statistics
    completed_tests = TestResult.query.filter_by(
        participant_id=user_id,
        status='completed'
    ).all()
    
    all_tests = Test.query.all()
    tests_completed = len(completed_tests)
    tests_pending = len(all_tests) - tests_completed
    total_tests = len(all_tests)
    completion_percentage = int((tests_completed / total_tests * 100)) if total_tests > 0 else 0
    
    # Get recommended tests
    recommended_tests = []
    if user.screening_completed and user.synesthesia_type:
        recommended_tests = Test.query.filter_by(
            synesthesia_type=user.synesthesia_type
        ).all()
    else:
        # Show all tests if screening not completed
        recommended_tests = all_tests
    
    # Build synesthesia profile
    synesthesia_profile = None
    if completed_tests:
        types = list(set([Test.query.get(t.test_id).synesthesia_type for t in completed_tests]))
        avg_consistency = sum([t.consistency_score for t in completed_tests if t.consistency_score]) / len(completed_tests) if completed_tests else 0
        
        synesthesia_profile = {
            'types': types,
            'consistency_score': int(avg_consistency)
        }
    
    return render_template(
        'participant_dashboard.html',
        user=user,
        tests_completed=tests_completed,
        tests_pending=tests_pending,
        completion_percentage=completion_percentage,
        screening_completed=user.screening_completed,
        recommended_tests=recommended_tests,
        completed_tests=completed_tests,
        synesthesia_profile=synesthesia_profile
    )


# Researcher Routes
@app.route('/researcher/dashboard')
def researcher_dashboard():
    if 'user_id' not in session or session.get('user_role') != 'researcher':
        flash('Please login to access this page', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user = Researcher.query.get(user_id)
    
    # Get statistics
    total_participants = Participant.query.count()
    active_participants = Participant.query.filter_by(status='active').count()
    completed_tests = TestResult.query.filter_by(status='completed').count()
    synesthetes_identified = Participant.query.filter(
        Participant.synesthesia_type.isnot(None)
    ).count()
    
    # Get recent activity
    recent_results = TestResult.query.order_by(
        TestResult.completed_at.desc()
    ).limit(10).all()
    
    recent_activity = []
    for result in recent_results:
        if result.completed_at:
            participant = Participant.query.get(result.participant_id)
            test = Test.query.get(result.test_id)
            recent_activity.append({
                'participant_id': participant.participant_id,
                'test_name': test.name,
                'status': result.status,
                'date': result.completed_at.strftime('%Y-%m-%d %H:%M')
            })
    
    # Get synesthesia distribution
    synesthesia_distribution = {}
    participants_with_syn = Participant.query.filter(
        Participant.synesthesia_type.isnot(None)
    ).all()
    
    for p in participants_with_syn:
        syn_type = p.synesthesia_type
        if syn_type:
            synesthesia_distribution[syn_type] = synesthesia_distribution.get(syn_type, 0) + 1
    
    return render_template(
        'researcher_dashboard.html',
        user=user,
        total_participants=total_participants,
        active_participants=active_participants,
        completed_tests=completed_tests,
        synesthetes_identified=synesthetes_identified,
        recent_activity=recent_activity,
        synesthesia_distribution=synesthesia_distribution
    )


if __name__ == '__main__':
    app.run(debug=True)