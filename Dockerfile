FROM python:3.12.4-alpine

WORKDIR /haldis

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]
