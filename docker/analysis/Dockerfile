FROM python:3.10-slim-bullseye

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev python3-dev libpq-dev libyaml-dev gcc musl-dev wait-for-it git-all\
 && rm -rf /var/lib/apt/lists/* \
 && apt-get clean

RUN python -m pip install --upgrade pip

COPY analysis/requirements.txt .
RUN pip install --no-cache -r requirements.txt
COPY analysis/analysis_app.py .

RUN git config --global user.name "Analysis process"
RUN git config --global user.email "fakemail@fakemail.com"

WORKDIR /

CMD ["python", "analysis_app.py"]