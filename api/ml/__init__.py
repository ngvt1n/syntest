"""
Machine Learning Module for SYNTEST

This module provides neural network-based analysis tools for synesthesia research data.
Currently implements:
- Anomaly detection for screening test responses

Future extensions:
- Color test consistency classification
- Speed congruency analysis
"""

from .screening_anomaly_detector import ScreeningAnomalyDetector

__all__ = ['ScreeningAnomalyDetector']
__version__ = '1.0.0'



