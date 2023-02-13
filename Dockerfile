FROM python:3.10

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

ENV PYTHONUNBUFFERED 0
EXPOSE 80

COPY . /usr/src/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

