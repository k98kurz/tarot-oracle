"""Test custom feature loaders for Tarot Oracle."""

import os
import tempfile
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_invocation_loader_basic():
    """Test InvocationLoader basic functionality with local files."""
    print("Testing InvocationLoader basic functionality...")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        
        try:
            # Change to temp directory for local file testing
            os.chdir(temp_dir)
            
            # Create test invocation file
            test_invocation = "By the ancient powers, I seek guidance through these cards."
            inv_file = Path("test_invocation.txt")
            inv_file.write_text(test_invocation)
            
            # Test loading
            from tarot_oracle.loaders import InvocationLoader
            loader = InvocationLoader()
            loaded = loader.load_invocation("test_invocation")
            assert loaded == test_invocation, f"Expected '{test_invocation}', got '{loaded}'"
            
            # Test listing (empty, since we don't have global config dir set up)
            invocations = loader.list_invocations()
            assert isinstance(invocations, list), "Should return a list"
            
            print("✅ InvocationLoader basic tests passed!")
            
        finally:
            os.chdir(original_cwd)


def test_spread_loader_basic():
    """Test SpreadLoader basic functionality with local files.""" 
    print("Testing SpreadLoader basic functionality...")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        
        try:
            # Change to temp directory for local file testing
            os.chdir(temp_dir)
            
            # Create test spread configuration
            test_spread = {
                "name": "Test Spread",
                "description": "A simple test spread",
                "layout": [
                    {"position": 1, "meaning": "Past"},
                    {"position": 2, "meaning": "Present"},
                    {"position": 3, "meaning": "Future"}
                ]
            }
            
            spread_file = Path("test_spread.json")
            spread_file.write_text(json.dumps(test_spread, indent=2))
            
            # Test loading
            from tarot_oracle.loaders import SpreadLoader
            loader = SpreadLoader()
            loaded = loader.load_spread("test_spread")
            assert loaded is not None, "Failed to load test spread"
            assert loaded["name"] == "Test Spread", f"Expected name 'Test Spread', got '{loaded['name']}'"
            assert len(loaded["layout"]) == 3, f"Expected 3 positions, got {len(loaded['layout'])}"
            
            # Test listing (empty, since we don't have global config dir set up)
            spreads = loader.list_spreads()
            assert isinstance(spreads, list), "Should return a list"
            
            print("✅ SpreadLoader basic tests passed!")
            
        finally:
            os.chdir(original_cwd)


def test_spread_validation():
    """Test spread configuration validation."""
    print("Testing spread validation...")
    
    from tarot_oracle.loaders import SpreadLoader
    loader = SpreadLoader()
    
    # Test valid configuration
    valid_config = {
        "name": "Valid Spread",
        "layout": [{"position": 1, "meaning": "Test"}]
    }
    
    try:
        result = loader._validate_spread_config(valid_config, "test")
        assert result["name"] == "Valid Spread"
    except ValueError:
        assert False, "Valid config should not raise ValueError"
    
    # Test invalid configuration (missing name)
    invalid_config = {
        "layout": [{"position": 1, "meaning": "Test"}]
    }
    
    try:
        loader._validate_spread_config(invalid_config, "test")
        assert False, "Invalid config should raise ValueError"
    except ValueError as e:
        assert "name" in str(e)
    
    # Test invalid semantic variable
    invalid_semantic = {
        "name": "Invalid Semantic",
        "layout": [{"position": 1, "meaning": "Test"}],
        "semantics": [{"rule": "When ${invalid} appears, something happens"}]
    }
    
    try:
        loader._validate_spread_config(invalid_semantic, "test")
        assert False, "Invalid semantic variable should raise ValueError"
    except ValueError as e:
        assert "invalid" in str(e)
    
    print("✅ Spread validation tests passed!")


def test_path_traversal_prevention():
    """Test that path traversal attacks are prevented."""
    print("Testing path traversal prevention...")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        
        try:
            # Change to temp directory for local file testing
            os.chdir(temp_dir)
            
            # Create malicious files outside current directory
            Path("subdir").mkdir()
            malicious_file = Path("subdir") / "malicious.txt"
            malicious_file.write_text("This should not be accessible")
            
            # Test invocation loader
            from tarot_oracle.loaders import InvocationLoader
            inv_loader = InvocationLoader()
            result = inv_loader.load_invocation("../subdir/malicious")
            assert result is None, "Path traversal should be prevented"
            
            # Test spread loader
            from tarot_oracle.loaders import SpreadLoader
            spread_loader = SpreadLoader()
            result = spread_loader.load_spread("../subdir/malicious")
            assert result is None, "Path traversal should be prevented"
            
            print("✅ Path traversal prevention tests passed!")
            
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    try:
        test_invocation_loader_basic()
        test_spread_loader_basic()
        test_spread_validation()
        test_path_traversal_prevention()
        print("\n🎉 All loader tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)