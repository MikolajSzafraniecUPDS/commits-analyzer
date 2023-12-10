FROM python:3.10-slim-bullseye

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev python3-dev libpq-dev libyaml-dev gcc musl-dev wait-for-it git-all\
 && rm -rf /var/lib/apt/lists/* \
 && apt-get clean

RUN python -m pip install --upgrade pip

COPY dashboard/requirements.txt .
RUN pip install --no-cache -r requirements.txt
COPY dashboard/app.py .
COPY dashboard/dashboard_app.py .

RUN git config --global user.name "Dashboard"
RUN git config --global user.email "fakemail@fakemail.com"

WORKDIR /

CMD ["python", "dashboard_app.py"]