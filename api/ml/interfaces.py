"""
Abstract interfaces for ML models following SOLID principles.

These interfaces allow for easy swapping of implementations and facilitate testing.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from dataclasses import dataclass


@dataclass
class AnomalyReport:
    """
    Standard report format for anomaly detection results.
    
    Attributes:
        is_valid: Whether the data passes quality checks
        anomaly_score: Float between 0 (normal) and 1 (anomalous)
        confidence: Confidence in the assessment (0-1)
        issues: List of detected issues
        recommendation: Action recommendation (ACCEPT/REJECT/REVIEW)
        details: Additional diagnostic information
    """
    is_valid: bool
    anomaly_score: float
    confidence: float
    issues: List[str]
    recommendation: str
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary"""
        return {
            'is_valid': self.is_valid,
            'anomaly_score': round(self.anomaly_score, 4),
            'confidence': round(self.confidence, 4),
            'issues': self.issues,
            'recommendation': self.recommendation,
            'details': self.details
        }


class AnomalyDetectorInterface(ABC):
    """
    Abstract interface for anomaly detection models.
    
    Follows Single Responsibility Principle: only detects anomalies,
    does not perform classification or other analysis.
    """
    
    @abstractmethod
    def detect(self, data: Any) -> AnomalyReport:
        """
        Analyze data and return anomaly report.
        
        Args:
            data: Input data (format depends on implementation)
            
        Returns:
            AnomalyReport with detection results
        """
        pass
    
    @abstractmethod
    def extract_features(self, data: Any) -> List[float]:
        """
        Extract numerical features from raw data.
        
        Args:
            data: Raw input data
            
        Returns:
            List of numerical features
        """
        pass



