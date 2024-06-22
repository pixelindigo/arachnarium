FROM python:3.11-alpine

WORKDIR /opt/simplecrawler

COPY crawler.py requirements.txt .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "crawler.py"]
CMD ["http://web/"]
