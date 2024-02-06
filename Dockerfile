FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

WORKDIR /app

COPY src/requirements.txt /app/src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/src/requirements.txt

COPY src/ /app/src/

CMD ["uvicorn", "--app-dir=src", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]