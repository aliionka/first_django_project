FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# CMD ["python", "manage.py", "runserver"]
CMD ["gunicorn", "first_django_project.wsgi:application", "--bind", "0.0.0.0:8000"]