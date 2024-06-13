FROM python:3.8
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 8082
CMD ["python3", "main.py"]