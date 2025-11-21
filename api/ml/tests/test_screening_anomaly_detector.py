"""
Unit tests for screening anomaly detector.

Tests cover:
1. Feature extraction
2. Autoencoder training and inference
3. Anomaly detection logic
4. Model save/load functionality
"""

import numpy as np
import tempfile
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ml.screening_anomaly_detector import ScreeningAnomalyDetector, Autoencoder
from ml.data_generator import ScreeningDataGenerator
from ml.feature_extraction import ScreeningFeatureExtractor


class TestAutoencoder:
    """Test suite for Autoencoder model"""
    
    def test_initialization(self):
        """Test autoencoder initializes with correct architecture"""
        model = Autoencoder(input_dim=15, encoding_dims=[8, 4])
        
        # Check weights exist
        assert 'W_enc_0' in model.weights
        assert 'W_enc_1' in model.weights
        assert 'W_dec_0' in model.weights
        assert 'W_dec_1' in model.weights
        
        # Check shapes
        assert model.weights['W_enc_0'].shape == (15, 8)
        assert model.weights['W_enc_1'].shape == (8, 4)
    
    def test_forward_pass_shape(self):
        """Test forward pass produces correct output shape"""
        model = Autoencoder(input_dim=15, encoding_dims=[8, 4])
        X = np.random.randn(10, 15).astype(np.float32)
        
        output = model.forward(X)
        
        assert output.shape == (10, 15), f"Expected shape (10, 15), got {output.shape}"
    
    def test_encoding(self):
        """Test encoding to bottleneck"""
        model = Autoencoder(input_dim=15, encoding_dims=[8, 4])
        X = np.random.randn(10, 15).astype(np.float32)
        
        encoded = model.encode(X)
        
        assert encoded.shape == (10, 4), f"Expected bottleneck shape (10, 4), got {encoded.shape}"
    
    def test_reconstruction_error(self):
        """Test reconstruction error calculation"""
        model = Autoencoder(input_dim=15, encoding_dims=[8, 4])
        X = np.random.randn(10, 15).astype(np.float32)
        
        reconstructed = model.forward(X)
        errors = model.compute_reconstruction_error(X, reconstructed)
        
        assert errors.shape == (10,), f"Expected error shape (10,), got {errors.shape}"
        assert np.all(errors >= 0), "Reconstruction errors should be non-negative"
    
    def test_training_reduces_error(self):
        """Test that training reduces reconstruction error"""
        # Generate simple data
        generator = ScreeningDataGenerator(random_seed=42)
        X_train, y_train, _ = generator.generate_dataset(n_normal=100, n_anomalous=0)
        
        model = Autoencoder(input_dim=15, encoding_dims=[8, 4])
        
        # Compute initial error
        initial_recon = model.forward(X_train)
        initial_error = np.mean(model.compute_reconstruction_error(X_train, initial_recon))
        
        # Train
        model.fit(X_train, epochs=20, learning_rate=0.01, batch_size=32, verbose=False)
        
        # Compute final error
        final_recon = model.forward(X_train)
        final_error = np.mean(model.compute_reconstruction_error(X_train, final_recon))
        
        assert final_error < initial_error, \
            f"Training should reduce error: initial={initial_error:.6f}, final={final_error:.6f}"
    
    def test_save_load(self):
        """Test model save and load"""
        model = Autoencoder(input_dim=15, encoding_dims=[8, 4])
        
        # Train briefly
        X = np.random.randn(50, 15).astype(np.float32)
        model.fit(X, epochs=5, verbose=False)
        
        # Save
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp:
            tmp_path = tmp.name
        
        try:
            model.save(tmp_path)
            
            # Load into new model
            model2 = Autoencoder(input_dim=15, encoding_dims=[8, 4])
            model2.load(tmp_path)
            
            # Check weights match
            for key in model.weights:
                assert np.allclose(model.weights[key], model2.weights[key]), \
                    f"Weights {key} don't match after load"
        
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestScreeningFeatureExtractor:
    """Test suite for feature extraction"""
    
    def test_feature_count(self):
        """Test that correct number of features are extracted"""
        extractor = ScreeningFeatureExtractor()
        
        # Mock session data
        session_data = {
            'session': None,
            'health': None,
            'definition': None,
            'pain_emotion': None,
            'type_choice': None,
            'events': []
        }
        
        features = extractor.extract(session_data)
        
        assert features.shape == (15,), f"Expected 15 features, got {features.shape}"
    
    def test_feature_names(self):
        """Test that feature names are available"""
        extractor = ScreeningFeatureExtractor()
        names = extractor.get_feature_names()
        
        assert len(names) == 15, f"Expected 15 feature names, got {len(names)}"
        assert 'avg_response_time_sec' in names
        assert 'completion_rate' in names


class TestScreeningAnomalyDetector:
    """Test suite for complete anomaly detector"""
    
    def test_initialization(self):
        """Test detector initializes correctly"""
        detector = ScreeningAnomalyDetector()
        
        assert detector.feature_extractor is not None
        assert detector.autoencoder is not None
        assert detector.threshold is None  # Not trained yet
    
    def test_training(self):
        """Test detector training"""
        # Generate training data
        generator = ScreeningDataGenerator(random_seed=42)
        X_train, y_train, _ = generator.generate_dataset(n_normal=100, n_anomalous=20)
        
        # Train detector
        detector = ScreeningAnomalyDetector()
        X_train_normal = X_train[y_train == 0]
        
        detector.fit(X_train_normal, epochs=20, verbose=False)
        
        # Check that threshold was set
        assert detector.threshold is not None, "Threshold should be set after training"
        assert detector.threshold > 0, "Threshold should be positive"
        assert detector.feature_means is not None
        assert detector.feature_stds is not None
    
    def test_anomaly_detection(self):
        """Test that detector can distinguish normal from anomalous"""
        # Generate data
        generator = ScreeningDataGenerator(random_seed=42)
        X_train, y_train, _ = generator.generate_dataset(n_normal=200, n_anomalous=0)
        X_test, y_test, test_sessions = generator.generate_dataset(
            n_normal=50,
            n_anomalous=50
        )
        
        # Train detector
        detector = ScreeningAnomalyDetector()
        detector.fit(X_train, epochs=50, learning_rate=0.001, verbose=False)
        
        # Test on normal examples
        normal_features = X_test[y_test == 0]
        normal_scores = []
        for i in range(len(normal_features)):
            session_data = {'session': None, 'health': None, 'definition': None,
                          'pain_emotion': None, 'type_choice': None, 'events': []}
            # Manually inject features
            detector.extract_features = lambda x: normal_features[i]
            report = detector.detect(session_data)
            normal_scores.append(report.anomaly_score)
        
        # Test on anomalous examples
        anomalous_features = X_test[y_test == 1]
        anomalous_scores = []
        for i in range(len(anomalous_features)):
            session_data = {'session': None, 'health': None, 'definition': None,
                          'pain_emotion': None, 'type_choice': None, 'events': []}
            detector.extract_features = lambda x: anomalous_features[i]
            report = detector.detect(session_data)
            anomalous_scores.append(report.anomaly_score)
        
        # Anomalous should generally have higher scores
        avg_normal = np.mean(normal_scores)
        avg_anomalous = np.mean(anomalous_scores)
        
        assert avg_anomalous > avg_normal, \
            f"Anomalous examples should have higher scores: normal={avg_normal:.4f}, anomalous={avg_anomalous:.4f}"
    
    def test_report_structure(self):
        """Test that anomaly report has correct structure"""
        generator = ScreeningDataGenerator(random_seed=42)
        X_train, _, _ = generator.generate_dataset(n_normal=100, n_anomalous=0)
        
        detector = ScreeningAnomalyDetector()
        detector.fit(X_train, epochs=10, verbose=False)
        
        # Create test session data
        session_data = {
            'session': None,
            'health': None,
            'definition': None,
            'pain_emotion': None,
            'type_choice': None,
            'events': []
        }
        
        report = detector.detect(session_data)
        
        # Check report structure
        assert hasattr(report, 'is_valid')
        assert hasattr(report, 'anomaly_score')
        assert hasattr(report, 'confidence')
        assert hasattr(report, 'issues')
        assert hasattr(report, 'recommendation')
        assert hasattr(report, 'details')
        
        # Check types
        assert isinstance(report.is_valid, bool)
        assert isinstance(report.anomaly_score, float)
        assert isinstance(report.confidence, float)
        assert isinstance(report.issues, list)
        assert isinstance(report.recommendation, str)
        assert isinstance(report.details, dict)
        
        # Check value ranges
        assert 0 <= report.confidence <= 1
        assert report.anomaly_score >= 0
        assert report.recommendation in ['ACCEPT', 'REVIEW', 'REJECT']
    
    def test_save_load_detector(self):
        """Test saving and loading complete detector"""
        # Train detector
        generator = ScreeningDataGenerator(random_seed=42)
        X_train, _, _ = generator.generate_dataset(n_normal=100, n_anomalous=0)
        
        detector = ScreeningAnomalyDetector()
        detector.fit(X_train, epochs=10, verbose=False)
        
        # Save
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = os.path.join(tmpdir, 'test_model.pkl')
            detector.save_model(model_path)
            
            # Load
            detector2 = ScreeningAnomalyDetector(model_path=model_path)
            
            # Check parameters match
            assert detector2.threshold == detector.threshold
            assert np.allclose(detector2.feature_means, detector.feature_means)
            assert np.allclose(detector2.feature_stds, detector.feature_stds)


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])



