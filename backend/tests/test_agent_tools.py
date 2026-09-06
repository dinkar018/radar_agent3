"""
Unit tests for LangGraph agent tools and regex extraction.
"""
from app.agent.tools import extract_code_from_response, format_data_description
import os
import numpy as np

def test_extract_code_from_markdown():
    markdown_text = """
Here is the code to process the radar data:
```python
import numpy as np

def process_radar():
    data = np.load('/data/sar_data.npy')
    print("Shape:", data.shape)
```
Let me know if this works!
"""
    code = extract_code_from_response(markdown_text)
    assert "import numpy as np" in code
    assert "def process_radar():" in code
    assert "```" not in code

def test_extract_code_raw_fallback():
    raw_code = "import numpy as np\nprint('Hello radar')"
    extracted = extract_code_from_response(raw_code)
    assert extracted.strip() == raw_code.strip()

def test_format_data_description(tmp_path):
    test_array = np.zeros((10, 20, 256), dtype=np.complex64)
    file_path = str(tmp_path / "test_sar.npy")
    np.save(file_path, test_array)
    
    desc = format_data_description([file_path])
    assert "test_sar.npy" in desc
    assert "(10, 20, 256)" in desc
    assert "complex64" in desc
