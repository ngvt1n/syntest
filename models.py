# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ColorStimulus(db.Model):
    """
    Minimal stimulus table for the Color test only.

    Columns reflect your diagram:
      - id (PK)
      - set_id (int; keep simple for now, no FK)
      - description (nullable)
      - owner_researcher_id (int; no FK)
      - family ('color' fixed)
      - r, g, b (0–255 ints)
      - trigger_type (nullable string; e.g., 'swatch', 'wheel', etc.)
    """
    __tablename__ = "color_stimuli"

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.Integer, nullable=True, index=True)
    description = db.Column(db.String(255), nullable=True)
    owner_researcher_id = db.Column(db.Integer, nullable=True, index=True)

    # fixed family
    family = db.Column(db.String(32), nullable=False, default="color")

    # rgb values as ints
    r = db.Column(db.Integer, nullable=False)
    g = db.Column(db.Integer, nullable=False)
    b = db.Column(db.Integer, nullable=False)

    trigger_type = db.Column(db.String(64), nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "set_id": self.set_id,
            "description": self.description,
            "owner_researcher_id": self.owner_researcher_id,
            "family": self.family,
            "r": self.r,
            "g": self.g,
            "b": self.b,
            "hex": f"#{self.r:02x}{self.g:02x}{self.b:02x}",
            "trigger_type": self.trigger_type,
        }


class ColorTrial(db.Model):
    """
    Stores what the participant did on each trial.

      - participant_id: string you pass from the UI (or leave null)
      - stimulus_id: FK -> ColorStimulus.id (nullable-safe commit)
      - trial_index: order in the session
      - selected_r/g/b: user's match/answer (if your slider outputs RGB)
      - response_ms: latency
      - meta_json: ONLY the four whitelisted fields (phase, repetition,
                   stimulus_label, display_rgb)
    """
    __tablename__ = "color_trials"

    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(64), nullable=True, index=True)

    stimulus_id = db.Column(
        db.Integer,
        db.ForeignKey("color_stimuli.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    stimulus = db.relationship("ColorStimulus", lazy="joined")

    trial_index = db.Column(db.Integer, nullable=True)

    selected_r = db.Column(db.Integer, nullable=True)
    selected_g = db.Column(db.Integer, nullable=True)
    selected_b = db.Column(db.Integer, nullable=True)

    response_ms = db.Column(db.Integer, nullable=True)

    meta_json = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "participant_id": self.participant_id,
            "stimulus_id": self.stimulus_id,
            "trial_index": self.trial_index,
            "selected_r": self.selected_r,
            "selected_g": self.selected_g,
            "selected_b": self.selected_b,
            "response_ms": self.response_ms,
            "meta_json": self.meta_json or {},
            "created_at": self.created_at.isoformat(),
        }
        
class TestData(db.Model):
    """
    Represents aggregated test-level data (e.g., Color Consistency Test results).
    Each ColorStimulus can be linked to many TestData entries.
    """
    __tablename__ = "test_data"

    # --- Keys and relationships ---
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), index=True, nullable=True)
    test_id = db.Column(db.Integer, nullable=True, index=True)
    owner_researcher_id = db.Column(db.Integer, nullable=True, index=True)
    session_id = db.Column(db.Integer, nullable=True, index=True)

    # Link to color stimulus (one-to-many from ColorStimulus)
    stimulus_id = db.Column(
        db.Integer,
        db.ForeignKey("color_stimuli.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    stimulus = db.relationship("ColorStimulus", backref="test_data")

    # --- Descriptive fields ---
    test_type = db.Column(db.String(64), nullable=True)  # e.g., "CCT", "SCT"
    stimulus_type = db.Column(db.String(64), nullable=True)
    family = db.Column(db.String(16), nullable=False, default="color")  # 'color', 'gustatory', 'space'
    locale = db.Column(db.String(16), nullable=True)

    # --- Core test metadata ---
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    trial = db.Column(db.Integer, nullable=True)
    cct_cutoff = db.Column(db.Float, nullable=True)
    cct_triggers = db.Column(db.Integer, nullable=True)
    cct_trials_per_trigger = db.Column(db.Integer, nullable=True)
    cct_valid = db.Column(db.Integer, nullable=True)

    # --- Consistency metrics ---
    cct_none_pct = db.Column(db.Float, nullable=True)
    cct_rt_mean = db.Column(db.Integer, nullable=True)
    cct_mean = db.Column(db.Float, nullable=True)
    cct_std = db.Column(db.Float, nullable=True)
    cct_median = db.Column(db.Float, nullable=True)

    # --- Complex data ---
    cct_per_trigger = db.Column(db.JSON, nullable=True)
    cct_pairwise = db.Column(db.JSON, nullable=True)

    # --- Results summary ---
    cct_pass = db.Column(db.Boolean, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "test_id": self.test_id,
            "owner_researcher_id": self.owner_researcher_id,
            "session_id": self.session_id,
            "stimulus_id": self.stimulus_id,
            "test_type": self.test_type,
            "stimulus_type": self.stimulus_type,
            "family": self.family,
            "locale": self.locale,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "trial": self.trial,
            "cct_cutoff": self.cct_cutoff,
            "cct_triggers": self.cct_triggers,
            "cct_trials_per_trigger": self.cct_trials_per_trigger,
            "cct_valid": self.cct_valid,
            "cct_none_pct": self.cct_none_pct,
            "cct_rt_mean": self.cct_rt_mean,
            "cct_mean": self.cct_mean,
            "cct_std": self.cct_std,
            "cct_median": self.cct_median,
            "cct_per_trigger": self.cct_per_trigger,
            "cct_pairwise": self.cct_pairwise,
            "cct_pass": self.cct_pass,
        }

