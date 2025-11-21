"""
Flask API blueprint for Machine Learning endpoints.

Provides anomaly detection services for screening test data.

Endpoints:
- POST /api/ml/check-screening-quality: Analyze screening session for anomalies
"""

from flask import Blueprint, request, jsonify, current_app
from models import (
    db, ScreeningSession, ScreeningHealth, ScreeningDefinition,
    ScreeningPainEmotion, ScreeningTypeChoice, ScreeningEvent
)
from ml.screening_anomaly_detector import ScreeningAnomalyDetector
import os


# Create blueprint
ml_bp = Blueprint("ml", __name__, url_prefix="/api/ml")

# Global detector instance (loaded once at startup)
_detector = None


def get_detector():
    """
    Get or initialize the anomaly detector.
    
    Singleton pattern to avoid loading model on every request.
    """
    global _detector
    
    if _detector is None:
        # Find the most recent trained model
        models_dir = os.path.join(
            os.path.dirname(__file__),
            'ml',
            'models'
        )
        
        if os.path.exists(models_dir):
            model_files = [f for f in os.listdir(models_dir) if f.endswith('.pkl') and 'params' not in f]
            if model_files:
                # Get most recent model
                model_files.sort(reverse=True)
                model_path = os.path.join(models_dir, model_files[0])
                
                current_app.logger.info(f"Loading anomaly detector from {model_path}")
                _detector = ScreeningAnomalyDetector(model_path=model_path)
                current_app.logger.info("Anomaly detector loaded successfully")
                return _detector
        
        # If no trained model found, return None
        current_app.logger.warning("No trained anomaly detection model found")
        return None
    
    return _detector


@ml_bp.route('/check-screening-quality', methods=['POST'])
def check_screening_quality():
    """
    Analyze a screening session for anomalous behavior patterns.
    
    Request Body:
        {
            "session_id": int  # ScreeningSession ID
        }
    
    Response:
        {
            "is_valid": bool,
            "anomaly_score": float,
            "confidence": float,
            "issues": [str],
            "recommendation": str,  # "ACCEPT", "REVIEW", or "REJECT"
            "details": {...}
        }
    
    Status Codes:
        200: Analysis successful
        400: Invalid request
        404: Session not found
        500: Server error
        503: ML model not available
    """
    try:
        # Parse request
        data = request.get_json()
        if not data or 'session_id' not in data:
            return jsonify({
                'error': 'Missing required field: session_id'
            }), 400
        
        session_id = data['session_id']
        
        # Get detector
        detector = get_detector()
        if detector is None:
            return jsonify({
                'error': 'Anomaly detection model not available',
                'message': 'The ML model has not been trained yet. Please run training script first.'
            }), 503
        
        # Fetch screening session from database
        session = ScreeningSession.query.get(session_id)
        if not session:
            return jsonify({
                'error': f'Screening session {session_id} not found'
            }), 404
        
        # Fetch related data
        health = ScreeningHealth.query.filter_by(session_id=session_id).first()
        definition = ScreeningDefinition.query.filter_by(session_id=session_id).first()
        pain_emotion = ScreeningPainEmotion.query.filter_by(session_id=session_id).first()
        type_choice = ScreeningTypeChoice.query.filter_by(session_id=session_id).first()
        events = ScreeningEvent.query.filter_by(session_id=session_id).order_by(
            ScreeningEvent.created_at
        ).all()
        
        # Prepare data for detector
        session_data = {
            'session': session,
            'health': health,
            'definition': definition,
            'pain_emotion': pain_emotion,
            'type_choice': type_choice,
            'events': events
        }
        
        # Run anomaly detection
        report = detector.detect(session_data)
        
        # Return results
        return jsonify(report.to_dict()), 200
    
    except Exception as e:
        current_app.logger.error(f"Error in check_screening_quality: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@ml_bp.route('/model-status', methods=['GET'])
def model_status():
    """
    Get status of the anomaly detection model.
    
    Response:
        {
            "model_loaded": bool,
            "model_path": str,
            "threshold": float,
            "feature_count": int
        }
    """
    try:
        detector = get_detector()
        
        if detector is None:
            return jsonify({
                'model_loaded': False,
                'message': 'No trained model available'
            }), 200
        
        return jsonify({
            'model_loaded': True,
            'threshold': float(detector.threshold) if detector.threshold else None,
            'feature_count': len(detector.feature_extractor.get_feature_names()),
            'feature_names': detector.feature_extractor.get_feature_names()
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error in model_status: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500


@ml_bp.route('/batch-check', methods=['POST'])
def batch_check():
    """
    Analyze multiple screening sessions in batch.
    
    Request Body:
        {
            "session_ids": [int, int, ...]
        }
    
    Response:
        {
            "results": [
                {
                    "session_id": int,
                    "is_valid": bool,
                    "anomaly_score": float,
                    ...
                },
                ...
            ],
            "summary": {
                "total": int,
                "valid": int,
                "anomalous": int,
                "needs_review": int
            }
        }
    """
    try:
        data = request.get_json()
        if not data or 'session_ids' not in data:
            return jsonify({
                'error': 'Missing required field: session_ids'
            }), 400
        
        session_ids = data['session_ids']
        if not isinstance(session_ids, list):
            return jsonify({
                'error': 'session_ids must be a list'
            }), 400
        
        # Get detector
        detector = get_detector()
        if detector is None:
            return jsonify({
                'error': 'Anomaly detection model not available'
            }), 503
        
        results = []
        summary = {'total': len(session_ids), 'valid': 0, 'anomalous': 0, 'needs_review': 0}
        
        for session_id in session_ids:
            # Fetch session and related data
            session = ScreeningSession.query.get(session_id)
            if not session:
                results.append({
                    'session_id': session_id,
                    'error': 'Session not found'
                })
                continue
            
            health = ScreeningHealth.query.filter_by(session_id=session_id).first()
            definition = ScreeningDefinition.query.filter_by(session_id=session_id).first()
            pain_emotion = ScreeningPainEmotion.query.filter_by(session_id=session_id).first()
            type_choice = ScreeningTypeChoice.query.filter_by(session_id=session_id).first()
            events = ScreeningEvent.query.filter_by(session_id=session_id).order_by(
                ScreeningEvent.created_at
            ).all()
            
            session_data = {
                'session': session,
                'health': health,
                'definition': definition,
                'pain_emotion': pain_emotion,
                'type_choice': type_choice,
                'events': events
            }
            
            # Run detection
            report = detector.detect(session_data)
            
            result = report.to_dict()
            result['session_id'] = session_id
            results.append(result)
            
            # Update summary
            if report.is_valid:
                summary['valid'] += 1
            else:
                summary['anomalous'] += 1
                if report.recommendation == 'REVIEW':
                    summary['needs_review'] += 1
        
        return jsonify({
            'results': results,
            'summary': summary
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error in batch_check: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500



