import os
import tempfile
from src.server_tools import analyze_local_logs

def test_analyze_local_logs_success():
    # Create a temporary log file with sample content
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as tmp:
        tmp.write("INFO: System startup successful.\n")
        tmp.write("ERROR: Connection timeout on port 5432.\n")
        tmp.write("WARNING: High memory usage detected.\n")
        tmp_path = tmp.name

    try:
        # Test finding a matching keyword
        result = analyze_local_logs(tmp_path, "error")
        assert "Connection timeout" in result
        assert "Found 1 matching lines" in result
    finally:
        os.unlink(tmp_path)

def test_analyze_local_logs_nonexistent_path():
    # Test handling of missing log files gracefully
    result = analyze_local_logs("/nonexistent/path/app.log", "error")
    assert "does not exist inside the container" in result
