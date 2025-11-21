"""
Unit tests for synthetic data generator.

Tests ensure:
1. Proper statistical distributions
2. Balanced dataset generation
3. Anomaly types are correctly injected
4. Reproducibility with random seeds
"""

import numpy as np
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ml.data_generator import ScreeningDataGenerator


class TestScreeningDataGenerator:
    """Test suite for ScreeningDataGenerator"""
    
    def test_initialization(self):
        """Test generator initializes correctly"""
        generator = ScreeningDataGenerator(random_seed=42)
        assert generator.rng is not None
        assert 'rushed' in generator.anomaly_patterns
        assert 'bot' in generator.anomaly_patterns
        assert 'distracted' in generator.anomaly_patterns
        assert 'inconsistent' in generator.anomaly_patterns
    
    def test_reproducibility(self):
        """Test that same seed produces same data"""
        gen1 = ScreeningDataGenerator(random_seed=42)
        gen2 = ScreeningDataGenerator(random_seed=42)
        
        X1, y1, _ = gen1.generate_dataset(n_normal=10, n_anomalous=5)
        X2, y2, _ = gen2.generate_dataset(n_normal=10, n_anomalous=5)
        
        assert np.allclose(X1, X2), "Same seed should produce identical data"
        assert np.array_equal(y1, y2), "Labels should match"
    
    def test_dataset_shape(self):
        """Test that generated dataset has correct shape"""
        generator = ScreeningDataGenerator(random_seed=42)
        
        n_normal = 100
        n_anomalous = 25
        
        X, y, sessions = generator.generate_dataset(
            n_normal=n_normal,
            n_anomalous=n_anomalous
        )
        
        # Check shapes
        assert X.shape == (n_normal + n_anomalous, 15), f"Expected shape ({n_normal + n_anomalous}, 15), got {X.shape}"
        assert y.shape == (n_normal + n_anomalous,), f"Expected shape ({n_normal + n_anomalous},), got {y.shape}"
        assert len(sessions) == n_normal + n_anomalous
    
    def test_label_distribution(self):
        """Test that labels are correctly balanced"""
        generator = ScreeningDataGenerator(random_seed=42)
        
        n_normal = 80
        n_anomalous = 20
        
        X, y, sessions = generator.generate_dataset(
            n_normal=n_normal,
            n_anomalous=n_anomalous
        )
        
        assert np.sum(y == 0) == n_normal, f"Expected {n_normal} normal examples, got {np.sum(y == 0)}"
        assert np.sum(y == 1) == n_anomalous, f"Expected {n_anomalous} anomalous examples, got {np.sum(y == 1)}"
    
    def test_feature_ranges(self):
        """Test that features are within reasonable ranges"""
        generator = ScreeningDataGenerator(random_seed=42)
        X, y, _ = generator.generate_dataset(n_normal=100, n_anomalous=25)
        
        # Check that features are non-negative
        assert np.all(X >= -0.01), "Features should be non-negative (small tolerance for float errors)"
        
        # Check specific feature ranges
        avg_rt = X[:, 0]
        assert np.all(avg_rt > 0), "Average response time should be positive"
        
        pct_too_fast = X[:, 5]
        pct_too_slow = X[:, 6]
        assert np.all((pct_too_fast >= 0) & (pct_too_fast <= 1)), "Percentages should be in [0, 1]"
        assert np.all((pct_too_slow >= 0) & (pct_too_slow <= 1)), "Percentages should be in [0, 1]"
        
        completion_rate = X[:, 14]
        assert np.all((completion_rate >= 0) & (completion_rate <= 1.01)), "Completion rate should be in [0, 1]"
    
    def test_normal_vs_anomalous_separation(self):
        """Test that anomalous examples differ from normal ones"""
        generator = ScreeningDataGenerator(random_seed=42)
        X, y, _ = generator.generate_dataset(n_normal=100, n_anomalous=100)
        
        X_normal = X[y == 0]
        X_anomalous = X[y == 1]
        
        # At least some features should have different distributions
        # Compare average response times
        avg_rt_normal = np.mean(X_normal[:, 0])
        avg_rt_anomalous = np.mean(X_anomalous[:, 0])
        
        # Anomalous should generally be different (either faster or slower)
        # Not checking specific direction since mixed anomaly types
        assert avg_rt_normal != avg_rt_anomalous, "Normal and anomalous should have different avg RT"
    
    def test_anomaly_type_distribution(self):
        """Test that anomaly types are distributed as specified"""
        generator = ScreeningDataGenerator(random_seed=42)
        
        distribution = {
            'rushed': 0.5,
            'bot': 0.3,
            'distracted': 0.1,
            'inconsistent': 0.1
        }
        
        _, _, sessions = generator.generate_dataset(
            n_normal=100,
            n_anomalous=100,
            anomaly_distribution=distribution
        )
        
        # Count anomaly types
        anomaly_sessions = [s for s in sessions if s.label == 'anomalous']
        type_counts = {}
        for s in anomaly_sessions:
            type_counts[s.anomaly_type] = type_counts.get(s.anomaly_type, 0) + 1
        
        # Check rough proportions (allow ±10% tolerance)
        for anomaly_type, expected_prop in distribution.items():
            actual_count = type_counts.get(anomaly_type, 0)
            expected_count = 100 * expected_prop
            assert abs(actual_count - expected_count) <= 15, \
                f"{anomaly_type}: expected ~{expected_count}, got {actual_count}"
    
    def test_rushed_pattern(self):
        """Test that rushed anomalies have fast response times"""
        generator = ScreeningDataGenerator(random_seed=42)
        
        # Generate only rushed anomalies
        _, _, sessions = generator.generate_dataset(
            n_normal=10,
            n_anomalous=50,
            anomaly_distribution={'rushed': 1.0}
        )
        
        rushed_sessions = [s for s in sessions if s.anomaly_type == 'rushed']
        
        for session in rushed_sessions:
            avg_rt = session.features[0]  # Average response time
            assert avg_rt < 10.0, f"Rushed sessions should have fast RT, got {avg_rt}"
    
    def test_bot_pattern(self):
        """Test that bot anomalies have uniform timing"""
        generator = ScreeningDataGenerator(random_seed=42)
        
        _, _, sessions = generator.generate_dataset(
            n_normal=10,
            n_anomalous=50,
            anomaly_distribution={'bot': 1.0}
        )
        
        bot_sessions = [s for s in sessions if s.anomaly_type == 'bot']
        
        for session in bot_sessions:
            cv_rt = session.features[4]  # Coefficient of variation
            assert cv_rt < 0.3, f"Bot sessions should have low variance (CV), got {cv_rt}"
    
    def test_metadata_consistency(self):
        """Test that metadata matches features"""
        generator = ScreeningDataGenerator(random_seed=42)
        X, y, sessions = generator.generate_dataset(n_normal=50, n_anomalous=50)
        
        for i, session in enumerate(sessions):
            # Check that features array matches what's stored
            assert np.allclose(session.features, X[i]), \
                f"Session {i} features don't match dataset"
            
            # Check label consistency
            expected_label = 0 if session.label == 'normal' else 1
            assert y[i] == expected_label, \
                f"Session {i} label mismatch"


if __name__ == '__main__':
    # Run tests
    import pytest
    pytest.main([__file__, '-v'])



