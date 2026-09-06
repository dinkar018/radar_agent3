FROM python:3.11-slim
RUN pip install --no-cache-dir numpy scipy matplotlib pandas scikit-learn
RUN useradd -m sandbox
USER sandbox
WORKDIR /workspace
