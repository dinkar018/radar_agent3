FROM python:3.11-slim

# Install scientific and radar signal processing dependencies
RUN pip install --no-cache-dir \
    numpy \
    scipy \
    matplotlib \
    pandas \
    scikit-learn

# Create non-root user
RUN useradd -m -u 1000 sandbox && \
    mkdir -p /workspace /data /output && \
    chown -R sandbox:sandbox /workspace /data /output

USER sandbox
WORKDIR /workspace

CMD ["python", "executor.py"]
