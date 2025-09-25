# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 필수 빌드 도구(일부 환경에서 필요)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONUNBUFFERED=1

# Cloud Run은 8080 포트를 사용
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
