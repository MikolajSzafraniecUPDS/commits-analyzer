FROM python:3.10-slim-bullseye

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev python3-dev libpq-dev libyaml-dev gcc musl-dev wait-for-it git-all \
 && rm -rf /var/lib/apt/lists/* \
 && apt-get clean

RUN python -m pip install --upgrade pip

COPY ETL/requirements.txt .
COPY ETL/etl_app.py .
RUN pip install --no-cache -r requirements.txt

RUN git config --global user.name "ETL process"
RUN git config --global user.email "fakemail@fakemail.com"

RUN mkdir -p submodules_repo/submodules
WORKDIR submodules_repo
RUN git init

WORKDIR /

CMD ["python", "etl_app.py"]
