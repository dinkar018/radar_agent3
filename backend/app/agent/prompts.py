SYSTEM_PROMPT = """You are a radar signal processing expert. You specialize in implementing research paper algorithms in Python for the TI IWR1843BOOST radar platform. You write clean, well-documented Python code using numpy, scipy, matplotlib, and pandas."""

CODE_GENERATION_PROMPT = """Based on the following context, generate a Python script to implement the radar processing methodology.

Paper Methodology Context:
{paper_context}

Radar Hardware Context:
{radar_context}

Data Description:
{data_description}

Data File Paths:
{data_file_paths}

User Instructions:
{user_instructions}

Requirements:
- Save all plots as PNG to the /output/ directory.
- Print all numerical results to stdout.
- Use matplotlib with Agg backend (e.g., import matplotlib; matplotlib.use('Agg')).
- The data is provided as numpy arrays and should be loaded via np.load().
- You must handle the IWR1843BOOST's 3TX/4RX antenna configuration appropriately.

Return only the Python code within ```python ``` markdown blocks.
"""

ERROR_RECOVERY_PROMPT = """The previous generated code failed to execute properly.

Previous Generated Code:
```python
{generated_code}
```

Execution Error:
{execution_error}

Please analyze the error and provide a corrected version of the complete Python code. Return only the Python code within ```python ``` markdown blocks.
"""

REFLECTION_PROMPT = """Please analyze the execution output of the code.
If the results look valid and no errors occurred, state that it is complete.
If there are issues, identify them.
"""
