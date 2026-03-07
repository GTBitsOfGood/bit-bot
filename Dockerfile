FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn
COPY . .
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8080", "app:app"]