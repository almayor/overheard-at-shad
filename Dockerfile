FROM python:3.9
WORKDIR /app
ENV PYTHONUNBUFFERED True
COPY . ./
RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

CMD python3 main.py
