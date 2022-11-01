FROM python:3.10

WORKDIR balancer

COPY ./* .

RUN python -m pip install -r requirements.txt

CMD python run.py --port 8000 --config ./config.xml