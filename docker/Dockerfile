FROM python:3.8

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Python and Package Libraries
RUN apt-get update && apt-get install -y libpq-dev gcc postgresql-client \
    python3-dev musl-dev

# install dependencies
COPY ./requirements*.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt -r requirements_dev.txt

# copy project
COPY . .

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "acms.wsgi:application"]
