# Use lightweight Python base image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg sox curl wget git unzip && \
    pip install --upgrade pip

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy MFA models into container
WORKDIR /mfa_models
COPY acoustic_models/english_mfa.zip .
COPY dictionary/english_us_arpa.dict .

# Move models into expected MFA paths
RUN mkdir -p /root/.local/share/mfa/acoustic_models && \
    mkdir -p /root/.local/share/mfa/dictionary && \
    unzip english_mfa.zip -d /root/.local/share/mfa/acoustic_models && \
    cp english_us_arpa.dict /root/.local/share/mfa/dictionary/english_us_arpa.dict

# Set up your FastAPI app
WORKDIR /app
COPY . /app

# Expose API port and run app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
