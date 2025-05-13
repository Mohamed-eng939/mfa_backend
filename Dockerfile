# Base image with Python
FROM python:3.9-slim

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg sox git curl wget \
    && pip install --upgrade pip

# Install required Python libraries
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install MFA models
RUN mfa model download acoustic english && \
    mfa model download dictionary english

# Create app folder
WORKDIR /app
COPY . /app

# Expose port and run
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
