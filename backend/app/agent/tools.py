import re
import os
import numpy as np
from typing import List

def extract_code_from_response(text: str) -> str:
    """Extract Python code from markdown code blocks in LLM response."""
    pattern = r'```python\s*(.*?)\s*```'
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return matches[0]
    
    pattern = r'```\s*(.*?)\s*```'
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return matches[0]
        
    return text.strip()

def format_data_description(file_paths: List[str]) -> str:
    """Inspect numpy files and describe their shape/dtype."""
    description = []
    for path in file_paths:
        try:
            if os.path.exists(path) and path.endswith('.npy'):
                data = np.load(path, mmap_mode='r')
                description.append(f"File: {os.path.basename(path)}, Shape: {data.shape}, Dtype: {data.dtype}")
            else:
                description.append(f"File: {os.path.basename(path)} (Details unavailable)")
        except Exception as e:
            description.append(f"File: {os.path.basename(path)} (Error reading: {str(e)})")
            
    return "\n".join(description)
