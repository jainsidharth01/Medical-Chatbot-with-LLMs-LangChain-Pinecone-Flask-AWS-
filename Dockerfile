FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 🔥 Force modern resolver properly
RUN python -m pip install --upgrade pip setuptools wheel

# Verify pip version (debug line)
RUN pip --version

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "app.py"]