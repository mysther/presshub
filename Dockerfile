FROM python:3.12

WORKDIR /app

COPY src/requirements.txt /app/src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/src/requirements.txt

COPY src/ /app/src/

CMD ["uvicorn", "uvicorn", "--app-dir=src", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]