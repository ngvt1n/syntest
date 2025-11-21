"""
Synthetic screening data generator for training anomaly detection models.

Uses proper statistical methods to create realistic, low-bias training data:
- Normal participants: Based on expected genuine user behavior distributions
- Anomalous participants: Inject specific anomaly patterns

Statistical Methods Used:
1. Log-normal distribution for response times (realistic for human behavior)
2. Beta distribution for proportions and rates
3. Truncated normal for bounded values
4. Stratified sampling to ensure balanced representation

Reference:
- Luce, R. D. (1986). Response Times: Their Role in Inferring Elementary Mental Organization
- Ratcliff, R., & McKoon, G. (2008). The Diffusion Decision Model
"""

import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class SyntheticScreeningSession:
    """
    Synthetic screening session data matching real database structure.
    """
    features: np.ndarray
    label: str  # 'normal' or 'anomalous'
    anomaly_type: str  # e.g., 'rushed', 'bot', 'distracted', 'inconsistent'
    metadata: Dict


class ScreeningDataGenerator:
    """
    Generates synthetic screening test data with realistic distributions.
    
    Design Philosophy:
    - Normal data based on empirical psychological research
    - Anomalies represent realistic bot/rushed/distracted patterns
    - Balanced generation to avoid model bias
    """
    
    def __init__(self, random_seed: int = 42):
        """
        Initialize generator with reproducible random seed.
        
        Args:
            random_seed: Seed for numpy random generator (for reproducibility)
        """
        self.rng = np.random.RandomState(random_seed)
        
        # Statistical parameters based on cognitive psychology research
        # Response times follow log-normal distribution (typical for human RT)
        self.normal_rt_params = {
            'mean_log': 3.4,      # exp(3.4) ≈ 30 seconds avg
            'std_log': 0.6,       # Reasonable variance
            'min_rt': 2.0,        # Minimum realistic RT
            'max_rt': 180.0       # Maximum before considered distracted
        }
        
        # Anomaly-specific parameters
        self.anomaly_patterns = {
            'rushed': {
                'mean_log': 0.5,   # exp(0.5) ≈ 1.6 seconds (too fast)
                'std_log': 0.2,
                'description': 'Suspiciously fast responses, clicking through'
            },
            'bot': {
                'mean_log': 2.0,   # exp(2.0) ≈ 7.4 seconds
                'std_log': 0.05,   # Very low variance (uniform timing)
                'description': 'Uniform timing pattern characteristic of bots'
            },
            'distracted': {
                'mean_log': 5.0,   # exp(5.0) ≈ 148 seconds (very slow)
                'std_log': 0.8,
                'description': 'Very slow responses, user distracted/multitasking'
            },
            'inconsistent': {
                'mean_log': 3.4,   # Normal mean
                'std_log': 2.0,    # Very high variance
                'description': 'Erratic timing, mix of very fast and very slow'
            }
        }
    
    def generate_dataset(
        self, 
        n_normal: int = 800, 
        n_anomalous: int = 200,
        anomaly_distribution: Dict[str, float] = None
    ) -> Tuple[np.ndarray, np.ndarray, List[SyntheticScreeningSession]]:
        """
        Generate balanced dataset with normal and anomalous examples.
        
        Args:
            n_normal: Number of normal examples
            n_anomalous: Number of anomalous examples
            anomaly_distribution: Distribution of anomaly types
                                 e.g., {'rushed': 0.4, 'bot': 0.3, ...}
        
        Returns:
            Tuple of (features, labels, metadata)
            - features: (n_samples, 15) array
            - labels: (n_samples,) array (0=normal, 1=anomalous)
            - metadata: List of SyntheticScreeningSession objects
        """
        if anomaly_distribution is None:
            # Default: equal distribution across anomaly types
            anomaly_distribution = {
                'rushed': 0.25,
                'bot': 0.25,
                'distracted': 0.25,
                'inconsistent': 0.25
            }
        
        # Validate distribution sums to 1
        assert abs(sum(anomaly_distribution.values()) - 1.0) < 0.01, \
            "Anomaly distribution must sum to 1.0"
        
        all_sessions = []
        
        # Generate normal examples
        print(f"Generating {n_normal} normal examples...")
        for i in range(n_normal):
            session = self._generate_normal_session(session_id=i)
            all_sessions.append(session)
        
        # Generate anomalous examples (stratified by type)
        print(f"Generating {n_anomalous} anomalous examples...")
        for anomaly_type, proportion in anomaly_distribution.items():
            n_type = int(n_anomalous * proportion)
            for i in range(n_type):
                session = self._generate_anomalous_session(
                    anomaly_type=anomaly_type,
                    session_id=n_normal + i
                )
                all_sessions.append(session)
        
        # Shuffle to avoid ordering bias
        self.rng.shuffle(all_sessions)
        
        # Extract features and labels
        features = np.array([s.features for s in all_sessions])
        labels = np.array([1 if s.label == 'anomalous' else 0 for s in all_sessions])
        
        print(f"Generated {len(all_sessions)} total examples")
        print(f"  Normal: {np.sum(labels == 0)}")
        print(f"  Anomalous: {np.sum(labels == 1)}")
        
        return features, labels, all_sessions
    
    def _generate_normal_session(self, session_id: int) -> SyntheticScreeningSession:
        """
        Generate a normal screening session with realistic behavior.
        
        Based on assumptions:
        - Users read questions carefully (20-60 seconds per step)
        - Response times follow log-normal distribution
        - Health exclusions are rare (10% probability each)
        - Most understand synesthesia definition (70% yes, 20% maybe, 10% no)
        """
        # 1. Generate response times (log-normal distribution)
        n_steps = 5
        response_times = self._generate_lognormal_times(
            n_samples=n_steps,
            mean_log=self.normal_rt_params['mean_log'],
            std_log=self.normal_rt_params['std_log'],
            min_val=self.normal_rt_params['min_rt'],
            max_val=self.normal_rt_params['max_rt']
        )
        
        avg_rt = np.mean(response_times)
        std_rt = np.std(response_times)
        min_rt = np.min(response_times)
        max_rt = np.max(response_times)
        cv_rt = std_rt / avg_rt if avg_rt > 0 else 0
        pct_too_fast = np.sum(response_times < 2.0) / len(response_times)
        pct_too_slow = np.sum(response_times > 300.0) / len(response_times)
        
        # 2. Generate behavioral features
        # Health exclusions (rare: 10% each)
        health_sum = self.rng.binomial(3, 0.1)
        
        # Definition score (skewed toward yes)
        def_prob = self.rng.choice([0.0, 1.0, 2.0], p=[0.1, 0.2, 0.7])
        
        # Type selection (realistic: 1-3 types selected)
        type_count = self.rng.choice([1, 2, 3, 4], p=[0.3, 0.4, 0.2, 0.1])
        
        # Type diversity (beta distribution, tends toward moderate diversity)
        type_diversity = self.rng.beta(2, 2)  # Mean ≈ 0.5
        
        # Consent timing (normal: 5-30 seconds to read and check)
        consent_timing = self.rng.lognormal(2.5, 0.5)  # Mean ≈ 15 seconds
        consent_timing = np.clip(consent_timing, 2.0, 60.0)
        
        # 3. Generate navigation features
        # Event count (normal: 8-15 events for completing screening)
        event_count = self.rng.randint(8, 16)
        
        # Back navigation (rare in normal flow: 0-2 times)
        back_nav_count = self.rng.choice([0, 1, 2], p=[0.7, 0.2, 0.1])
        
        # Completion rate (most normal users complete: 80% fully complete)
        completion_rate = 1.0 if self.rng.rand() < 0.8 else self.rng.uniform(0.6, 1.0)
        
        features = np.array([
            avg_rt, std_rt, min_rt, max_rt, cv_rt, pct_too_fast, pct_too_slow,
            health_sum, def_prob, type_count, type_diversity, consent_timing,
            event_count, back_nav_count, completion_rate
        ], dtype=np.float32)
        
        return SyntheticScreeningSession(
            features=features,
            label='normal',
            anomaly_type='none',
            metadata={
                'session_id': session_id,
                'response_times': response_times.tolist(),
                'generation_method': 'lognormal',
                'description': 'Normal participant with realistic behavior'
            }
        )
    
    def _generate_anomalous_session(
        self, 
        anomaly_type: str, 
        session_id: int
    ) -> SyntheticScreeningSession:
        """
        Generate an anomalous screening session with specific pattern.
        
        Args:
            anomaly_type: One of 'rushed', 'bot', 'distracted', 'inconsistent'
            session_id: Unique identifier
        """
        params = self.anomaly_patterns[anomaly_type]
        n_steps = 5
        
        # Generate anomalous response times
        response_times = self._generate_lognormal_times(
            n_samples=n_steps,
            mean_log=params['mean_log'],
            std_log=params['std_log'],
            min_val=0.5,
            max_val=600.0
        )
        
        # Add specific anomaly characteristics
        if anomaly_type == 'rushed':
            # All responses very fast
            response_times = np.clip(response_times, 0.5, 3.0)
            
        elif anomaly_type == 'bot':
            # Extremely uniform timing
            base_time = response_times[0]
            response_times = base_time + self.rng.normal(0, 0.1, size=n_steps)
            response_times = np.abs(response_times)
            
        elif anomaly_type == 'distracted':
            # Mix of normal and very long pauses
            for i in range(len(response_times)):
                if self.rng.rand() < 0.4:  # 40% chance of long pause
                    response_times[i] = self.rng.uniform(180, 600)
        
        elif anomaly_type == 'inconsistent':
            # Wild swings between very fast and very slow
            for i in range(len(response_times)):
                if i % 2 == 0:
                    response_times[i] = self.rng.uniform(0.5, 2.0)  # Very fast
                else:
                    response_times[i] = self.rng.uniform(120, 300)  # Very slow
        
        # Calculate timing features
        avg_rt = np.mean(response_times)
        std_rt = np.std(response_times)
        min_rt = np.min(response_times)
        max_rt = np.max(response_times)
        cv_rt = std_rt / avg_rt if avg_rt > 0 else 0
        pct_too_fast = np.sum(response_times < 2.0) / len(response_times)
        pct_too_slow = np.sum(response_times > 300.0) / len(response_times)
        
        # Generate suspicious behavioral patterns
        if anomaly_type == 'rushed':
            # Rushed users skip reading, random answers
            health_sum = self.rng.randint(0, 4)  # Random health checks
            def_prob = self.rng.choice([0.0, 1.0, 2.0])  # Random
            type_count = self.rng.randint(0, 5)  # May select none or all
            type_diversity = self.rng.uniform(0, 1)
            consent_timing = self.rng.uniform(0.5, 2.0)  # Very fast consent
            event_count = self.rng.randint(5, 8)  # Minimal events
            back_nav_count = 0
            completion_rate = self.rng.uniform(0.4, 0.8)  # Often incomplete
            
        elif anomaly_type == 'bot':
            # Bots have systematic patterns
            health_sum = 0  # Never check health issues
            def_prob = 2.0  # Always "yes"
            type_count = 4  # Select all types
            type_diversity = 0.25  # All same frequency
            consent_timing = 5.0  # Fixed timing
            event_count = 10  # Exact count
            back_nav_count = 0  # Never go back
            completion_rate = 1.0  # Always complete
            
        else:
            # Other anomalies: use normal behavioral patterns with timing issues
            health_sum = self.rng.binomial(3, 0.1)
            def_prob = self.rng.choice([0.0, 1.0, 2.0], p=[0.1, 0.2, 0.7])
            type_count = self.rng.choice([1, 2, 3, 4], p=[0.3, 0.4, 0.2, 0.1])
            type_diversity = self.rng.beta(2, 2)
            consent_timing = self.rng.lognormal(2.5, 0.5)
            consent_timing = np.clip(consent_timing, 2.0, 60.0)
            event_count = self.rng.randint(8, 16)
            back_nav_count = self.rng.choice([0, 1, 2], p=[0.7, 0.2, 0.1])
            completion_rate = 1.0 if self.rng.rand() < 0.5 else self.rng.uniform(0.3, 0.8)
        
        features = np.array([
            avg_rt, std_rt, min_rt, max_rt, cv_rt, pct_too_fast, pct_too_slow,
            health_sum, def_prob, type_count, type_diversity, consent_timing,
            event_count, back_nav_count, completion_rate
        ], dtype=np.float32)
        
        return SyntheticScreeningSession(
            features=features,
            label='anomalous',
            anomaly_type=anomaly_type,
            metadata={
                'session_id': session_id,
                'response_times': response_times.tolist(),
                'anomaly_pattern': params['description'],
                'generation_method': f'lognormal_{anomaly_type}'
            }
        )
    
    def _generate_lognormal_times(
        self,
        n_samples: int,
        mean_log: float,
        std_log: float,
        min_val: float,
        max_val: float
    ) -> np.ndarray:
        """
        Generate response times from log-normal distribution (realistic for humans).
        
        Log-normal is used because:
        1. Response times are always positive
        2. Distribution is right-skewed (few very slow responses)
        3. Well-established in cognitive psychology literature
        
        Args:
            n_samples: Number of samples
            mean_log: Mean of underlying normal distribution
            std_log: Std of underlying normal distribution
            min_val: Minimum value (truncate below)
            max_val: Maximum value (truncate above)
        
        Returns:
            Array of response times in seconds
        """
        times = self.rng.lognormal(mean_log, std_log, size=n_samples)
        # Truncate to realistic bounds
        times = np.clip(times, min_val, max_val)
        return times
    
    def save_dataset(
        self, 
        features: np.ndarray, 
        labels: np.ndarray, 
        filepath: str
    ):
        """Save generated dataset to disk."""
        np.savez_compressed(
            filepath,
            features=features,
            labels=labels,
            feature_names=self._get_feature_names()
        )
        print(f"Dataset saved to {filepath}")
    
    def load_dataset(self, filepath: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load dataset from disk."""
        data = np.load(filepath)
        return data['features'], data['labels']
    
    def _get_feature_names(self) -> List[str]:
        """Return feature names for reference."""
        return [
            'avg_response_time_sec',
            'std_response_time_sec',
            'min_response_time_sec',
            'max_response_time_sec',
            'cv_response_time',
            'pct_too_fast',
            'pct_too_slow',
            'health_check_sum',
            'definition_score',
            'type_selection_count',
            'type_selection_diversity',
            'consent_timing_sec',
            'event_count',
            'back_navigation_count',
            'step_completion_rate'
        ]



