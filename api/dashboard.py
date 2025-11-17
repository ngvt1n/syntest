# api/dashboard.py
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, session
from models import db, Participant, Researcher, ColorStimulus, TestData

# Participant Dashboard Blueprint
participant_bp = Blueprint('participant_dashboard', __name__, url_prefix='/api/participant')

@participant_bp.route('/dashboard', methods=['GET'])
def get_participant_dashboard():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401

        user_id = session['user_id']
        role = session.get('user_role')

        if role != 'participant':
            return jsonify({'error': 'Not authorized'}), 403

        user = Participant.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': role
        }

        data = {
            "user": user_data,
            "tests_completed": 3,
            "tests_pending": 2,
            "completion_percentage": 60
        }
        return jsonify(data)
    except Exception as e:
        print(f"Error in get_participant_dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# Researcher Dashboard Blueprint
researcher_bp = Blueprint('researcher_dashboard', __name__, url_prefix='/api/researcher')

@researcher_bp.route('/dashboard/summary', methods=['GET'])
def get_researcher_dashboard_summary():
    try:
        if 'user_id' not in session or session.get('user_role') != 'researcher':
            return jsonify({'error': 'Not authenticated as researcher'}), 401

        # Total participants
        total_participants = Participant.query.count()

        # Active participants (logged in within last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        active_participants = Participant.query.filter(
            Participant.last_login >= seven_days_ago
        ).count()

        # Total stimuli
        total_stimuli = ColorStimulus.query.count()

        # Total completed tests
        tests_completed = TestData.query.count()

        return jsonify({
            'total_participants': total_participants,
            'active_participants': active_participants,
            'total_stimuli': total_stimuli,
            'tests_completed': tests_completed
        }), 200
    except Exception as e:
        print(f"Error in dashboard summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@researcher_bp.route('/dashboard/recent', methods=['GET'])
def get_researcher_dashboard_recent():
    try:
        if 'user_id' not in session or session.get('user_role') != 'researcher':
            return jsonify({'error': 'Not authenticated as researcher'}), 401

        # Recent participants (last 10)
        recent_participants = (
            Participant.query
            .order_by(Participant.created_at.desc())
            .limit(10)
            .all()
        )

        # Recent stimuli (last 10)
        recent_stimuli = (
            ColorStimulus.query
            .order_by(ColorStimulus.created_at.desc())
            .limit(10)
            .all()
        )

        # Format participants
        participants_data = [
            {
                'name': p.name,
                'email': p.email,
                'created_at': p.created_at.strftime('%Y-%m-%d %H:%M') if p.created_at else 'N/A'
            }
            for p in recent_participants
        ]

        # Format stimuli
        stimuli_data = [
            {
                'description': s.description or 'N/A',
                'family': s.family or 'N/A',
                'created_at': s.created_at.strftime('%Y-%m-%d %H:%M') if s.created_at else 'N/A'
            }
            for s in recent_stimuli
        ]

        return jsonify({
            'participants': participants_data,
            'stimuli': stimuli_data
        }), 200
    except Exception as e:
        print(f"Error in dashboard recent: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# Export both blueprints
# Note: We keep 'bp' for backward compatibility with participant routes
bp = participant_bp