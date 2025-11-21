"""
Integration tests for ML API endpoints.

Tests the complete flow from database to API response.
"""

import sys
import os
import pytest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Flask
from models import (
    db, ScreeningSession, ScreeningHealth, ScreeningDefinition,
    ScreeningPainEmotion, ScreeningTypeChoice, ScreeningEvent, YesNo, YesNoMaybe, Frequency
)
from ml_api import ml_bp
from ml.data_generator import ScreeningDataGenerator
from ml.screening_anomaly_detector import ScreeningAnomalyDetector


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    
    db.init_app(app)
    app.register_blueprint(ml_bp)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def trained_detector(app):
    """Create and train a detector for testing"""
    with app.app_context():
        generator = ScreeningDataGenerator(random_seed=42)
        X_train, _, _ = generator.generate_dataset(n_normal=100, n_anomalous=0)
        
        detector = ScreeningAnomalyDetector()
        detector.fit(X_train, epochs=20, verbose=False)
        
        # Save to models directory
        models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
        os.makedirs(models_dir, exist_ok=True)
        model_path = os.path.join(models_dir, 'test_model.pkl')
        detector.save_model(model_path)
        
        yield detector
        
        # Cleanup
        if os.path.exists(model_path):
            os.remove(model_path)
            params_path = model_path.replace('.pkl', '_params.pkl')
            if os.path.exists(params_path):
                os.remove(params_path)


def create_mock_screening_session(db_session, is_anomalous=False):
    """
    Create a mock screening session in the database.
    
    Args:
        db_session: SQLAlchemy session
        is_anomalous: If True, create suspicious patterns
    
    Returns:
        ScreeningSession object
    """
    # Create screening session
    session = ScreeningSession(
        participant_id=1,
        status='completed',
        consent_given=True,
        eligible=True
    )
    db_session.add(session)
    db_session.flush()
    
    # Create health data
    health = ScreeningHealth(
        session_id=session.id,
        drug_use=False,
        neuro_condition=False,
        medical_treatment=False
    )
    db_session.add(health)
    
    # Create definition
    definition = ScreeningDefinition(
        session_id=session.id,
        answer=YesNoMaybe.yes
    )
    db_session.add(definition)
    
    # Create pain/emotion
    pain_emotion = ScreeningPainEmotion(
        session_id=session.id,
        answer=YesNo.no
    )
    db_session.add(pain_emotion)
    
    # Create type choice
    type_choice = ScreeningTypeChoice(
        session_id=session.id,
        grapheme=Frequency.yes,
        music=Frequency.sometimes,
        lexical=Frequency.no,
        sequence=Frequency.no
    )
    db_session.add(type_choice)
    
    # Create events with realistic or anomalous timing
    base_time = datetime.utcnow() - timedelta(minutes=5)
    
    if is_anomalous:
        # Rushed: all events very close together (< 1 second apart)
        time_deltas = [0.5, 0.6, 0.5, 0.7, 0.5]
    else:
        # Normal: reasonable spacing (20-60 seconds apart)
        time_deltas = [30, 45, 25, 40, 35]
    
    current_time = base_time
    for step in range(5):
        event = ScreeningEvent(
            session_id=session.id,
            step=step,
            event=f'step_{step}_continue',
            created_at=current_time
        )
        db_session.add(event)
        current_time += timedelta(seconds=time_deltas[step])
    
    db_session.commit()
    return session


class TestMLAPIIntegration:
    """Integration tests for ML API"""
    
    def test_model_status_no_model(self, client):
        """Test model status when no model is loaded"""
        response = client.get('/api/ml/model-status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'model_loaded' in data
    
    def test_check_screening_quality_missing_session_id(self, client, trained_detector):
        """Test API returns error when session_id is missing"""
        response = client.post(
            '/api/ml/check-screening-quality',
            json={}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'session_id' in data['error']
    
    def test_check_screening_quality_session_not_found(self, client, trained_detector):
        """Test API returns 404 when session doesn't exist"""
        response = client.post(
            '/api/ml/check-screening-quality',
            json={'session_id': 9999}
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_check_screening_quality_normal_session(self, app, client, trained_detector):
        """Test detecting a normal screening session"""
        with app.app_context():
            # Create normal session
            session = create_mock_screening_session(db.session, is_anomalous=False)
            session_id = session.id
            
            response = client.post(
                '/api/ml/check-screening-quality',
                json={'session_id': session_id}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Check response structure
            assert 'is_valid' in data
            assert 'anomaly_score' in data
            assert 'confidence' in data
            assert 'issues' in data
            assert 'recommendation' in data
            assert 'details' in data
            
            # Normal session should be valid
            assert isinstance(data['is_valid'], bool)
            assert isinstance(data['anomaly_score'], (int, float))
            assert isinstance(data['confidence'], (int, float))
    
    def test_check_screening_quality_anomalous_session(self, app, client, trained_detector):
        """Test detecting an anomalous screening session"""
        with app.app_context():
            # Create anomalous (rushed) session
            session = create_mock_screening_session(db.session, is_anomalous=True)
            session_id = session.id
            
            response = client.post(
                '/api/ml/check-screening-quality',
                json={'session_id': session_id}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Rushed session should likely be flagged (though depends on threshold)
            assert 'anomaly_score' in data
            assert isinstance(data['issues'], list)
            assert data['recommendation'] in ['ACCEPT', 'REVIEW', 'REJECT']
    
    def test_batch_check(self, app, client, trained_detector):
        """Test batch checking multiple sessions"""
        with app.app_context():
            # Create multiple sessions
            session1 = create_mock_screening_session(db.session, is_anomalous=False)
            session2 = create_mock_screening_session(db.session, is_anomalous=True)
            session3 = create_mock_screening_session(db.session, is_anomalous=False)
            
            session_ids = [session1.id, session2.id, session3.id]
            
            response = client.post(
                '/api/ml/batch-check',
                json={'session_ids': session_ids}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Check response structure
            assert 'results' in data
            assert 'summary' in data
            
            # Check results count
            assert len(data['results']) == 3
            
            # Check summary
            summary = data['summary']
            assert 'total' in summary
            assert summary['total'] == 3
            assert 'valid' in summary
            assert 'anomalous' in summary
    
    def test_batch_check_invalid_input(self, client, trained_detector):
        """Test batch check with invalid input"""
        response = client.post(
            '/api/ml/batch-check',
            json={'session_ids': 'not_a_list'}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])



