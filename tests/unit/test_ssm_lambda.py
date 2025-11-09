import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'lambda'))
from ssm_reader_handler import generate_helm_values


class TestLambdaFunction:
    def test_development_returns_1_replica(self):
        """Development environment should return 1 replica."""
        result = generate_helm_values("development")
        assert result["ReplicaCount"] == "1"
    
    def test_staging_returns_2_replicas(self):
        """Staging environment should return 2 replicas."""
        result = generate_helm_values("staging")
        assert result["ReplicaCount"] == "2"
    
    def test_production_returns_2_replicas(self):
        """Production environment should return 2 replicas.""" 
        result = generate_helm_values("production")
        assert result["ReplicaCount"] == "2"
    
    def test_unknown_environment_defaults_to_1(self):
        """Unknown environments should default to 1 replica."""
        result = generate_helm_values("unknown")
        assert result["ReplicaCount"] == "1"
        
    def test_stage_returns_1_replica_fallback(self):
        """Stage environment should default to 1 replica (not in replica_map)."""
        result = generate_helm_values("stage") 
        assert result["ReplicaCount"] == "1"

    def test_case_sensitivity(self):
        """Test that environment matching is case-sensitive."""
        result_upper = generate_helm_values("STAGE")
        assert result_upper["ReplicaCount"] == "1"
    
    def test_empty_string_environment(self):
        """Test empty string environment defaults to 1."""
        result = generate_helm_values("")
        assert result["ReplicaCount"] == "1"
    
    def test_none_environment_handling(self):
        """Test None value handling (edge case)."""
        result = generate_helm_values(None)
        assert result["ReplicaCount"] == "1"
    
    def test_return_structure(self):
        """Test that function returns correct structure."""
        result = generate_helm_values("development")

        assert isinstance(result, dict)
        assert "ReplicaCount" in result
        assert isinstance(result["ReplicaCount"], str)
