FROM python:3.10

WORKDIR worker

COPY ./* .

RUN python -m pip install -r requirements.txt

CMD python run.py --port 8000