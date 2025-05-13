FROM python:3.9-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg sox curl unzip && \
    pip install --upgrade pip

# Install Python libraries
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create model folders
WORKDIR /mfa_models
RUN mkdir -p /root/.local/share/mfa/acoustic_models \
    /root/.local/share/mfa/dictionary

# Download and unzip English acoustic model
RUN curl -L -o english_mfa.zip 'https://drive.usercontent.google.com/download?id=1cK5HaiVu0PZaWoD61q_LlF0k7P47FxFW&confirm=t' && \
    unzip english_mfa.zip -d /root/.local/share/mfa/acoustic_models

# Download dictionary
RUN curl -L -o /root/.local/share/mfa/dictionary/english_us_arpa.dict 'https://drive.usercontent.google.com/download?id=14PVpBhZWeisRGV28Luh3Jb27aq0fICA1&confirm=t'

# Set up your app
WORKDIR /app
COPY . /app

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
