FROM python:3.10

WORKDIR /app

# Install system dependencies required for torch/scipy
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (better caching)
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies without cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the project
COPY . .

CMD ["python3", "app.py"]