FROM python:3.13-alpine

WORKDIR /app
COPY src/ /app

RUN pip install -r requirements.txt
RUN pip install gunicorn

ENV FLASK_ENV=production

EXPOSE 4200

CMD ["gunicorn", "--bind", "0.0.0.0:4200", "app:app"]