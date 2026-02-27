# Image with Python
FROM python:3.12-slim

# Creating app dir in container and getting inside
WORKDIR /app

# Installing Linux tools for setup
RUN apt-get update && apt-get install -y \
    # Compilator, some libs are in C
    gcc \
    # Instruction for gcc how to communicate with Python
    python3-dev \
    # Removing update info
    && rm -rf /var/lib/apt/lists/*

# Copy file to root dir
COPY requirements.txt .

# Install requirements, no cache in container needed
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all dirs
COPY . .

# Command to run after starting
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
