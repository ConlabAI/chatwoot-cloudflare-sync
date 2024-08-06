# Use Python 3.12 slim image as the base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ ./src/

# Expose port 8000
EXPOSE 8000

# Command to run the FastAPI application
CMD ["fastapi", "run", "src/api.py"]