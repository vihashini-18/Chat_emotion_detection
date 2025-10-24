# Use official lightweight Python image
FROM python:3.10-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED True

# Set working directory
WORKDIR /app

# Copy all files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Hugging Face default port
EXPOSE 7860

# Run your Flask app
CMD ["python", "app.py"]
