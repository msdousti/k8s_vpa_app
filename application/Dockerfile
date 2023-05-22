FROM python:alpine3.17

RUN pip install flask

COPY app.py /
WORKDIR /

EXPOSE 5000

CMD ["python", "app.py"]
