from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Participant(db.Model):
    """Model for study participants"""
    __tablename__ = 'participants'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    age = db.Column(db.Integer)
    country = db.Column(db.String(100))
    
    # Study-related fields
    screening_completed = db.Column(db.Boolean, default=False)
    synesthesia_type = db.Column(db.String(100))
    status = db.Column(db.String(50), default='active')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    test_results = db.relationship('TestResult', backref='participant', lazy=True)
    
    def __init__(self, **kwargs):
        super(Participant, self).__init__(**kwargs)
        # Generate unique participant ID
        if not self.participant_id:
            self.participant_id = f"P{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    def __repr__(self):
        return f'<Participant {self.participant_id}>'


class Researcher(db.Model):
    """Model for researchers"""
    __tablename__ = 'researchers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    institution = db.Column(db.String(200))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Researcher {self.email}>'


class Test(db.Model):
    """Model for different test types"""
    __tablename__ = 'tests'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    synesthesia_type = db.Column(db.String(100))
    duration = db.Column(db.Integer)  # in minutes
    
    # Relationships
    results = db.relationship('TestResult', backref='test', lazy=True)
    
    def __repr__(self):
        return f'<Test {self.name}>'


class TestResult(db.Model):
    """Model for test results"""
    __tablename__ = 'test_results'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    
    # Result data
    status = db.Column(db.String(50), default='not_started')  # not_started, in_progress, completed
    consistency_score = db.Column(db.Float)
    result_data = db.Column(db.JSON)  # Store test-specific results as JSON
    
    # Timestamps
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<TestResult P:{self.participant_id} T:{self.test_id}>'


class ScreeningResponse(db.Model):
    """Model for screening questionnaire responses"""
    __tablename__ = 'screening_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    
    # Screening results
    responses = db.Column(db.JSON)  # Store all questionnaire responses
    eligible = db.Column(db.Boolean)
    recommended_tests = db.Column(db.JSON)  # List of recommended test IDs
    
    # Timestamp
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ScreeningResponse {self.participant_id}>'