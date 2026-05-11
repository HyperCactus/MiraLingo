def test_cli_help():
    """Test mirad-translate --help runs without error."""
    import subprocess
    
    result = subprocess.run([
        "mirad-translate", "--help"
    ], capture_output=True)
    
    assert result.returncode == 0
    
    
# Test translation
# This requires the package to be installed
# and is omitted here as it would need subprocess
