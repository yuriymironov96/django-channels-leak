FROM python:3.9-slim
RUN apt-get update -q \
    && apt-get install -yq \
    libpq-dev \
    gcc \
    gettext \
    && pip install --upgrade pip \
    && pip install poetry

RUN mkdir /code
ADD . /code/
WORKDIR /code

RUN poetry install
CMD ["/bin/bash"]
