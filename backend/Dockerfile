FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (ensure they are available)
RUN playwright install --with-deps chromium

COPY . .

# Environment variables should be passed at runtime
ENV PYTHONPATH=/app

# Command will be overridden by docker-compose for api vs worker
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
