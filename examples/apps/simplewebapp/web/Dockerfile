FROM python:3.11-alpine

COPY server.py requirements.txt .

RUN pip install -r requirements.txt

ENTRYPOINT ["flask"]
CMD ["--app", "server", "run", "--host", "0.0.0.0", "--port", "80"]
