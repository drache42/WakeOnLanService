FROM python:3.13-slim-bookworm

WORKDIR /app
COPY src/ /app

RUN pip install -r requirements.txt
RUN pip install gunicorn

ENV FLASK_ENV=production

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]