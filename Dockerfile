FROM python:3.11.3
WORKDIR /app/documents/
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .