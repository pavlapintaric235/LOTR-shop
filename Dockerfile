FROM python:3.13-slim

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /code/requirements.txt

COPY . /code

EXPOSE 10000

CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"