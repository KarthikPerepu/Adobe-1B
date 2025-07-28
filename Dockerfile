# Filename: Dockerfile
FROM --platform=linux/amd64 python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy pre-downloaded model and source
COPY models models
COPY src src

# Default persona & job; override at runtime
ENV PERSONA="Investment Analyst"
ENV JOB="Analyze revenue trends, R&D investments, and market positioning strategies"

ENTRYPOINT ["python", "src/main.py"]