# Stage 1: Build stage
FROM python:3.13-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock* /app/

# Install Poetry
RUN pip install poetry

# Install dependencies without virtualenv
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --with production

# Copy the rest of the application code to the container
COPY src/ /app/

# Stage 2: Production stage
FROM python:3.13-alpine

# Set the working directory
WORKDIR /app

# Copy the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code from the builder stage
COPY --from=builder /app /app

# Set the FLASK environment variable
ENV FLASK_APP=wakeonlanservice/app:app
ENV FLASK_ENV=production

# Expose the port the app runs on
EXPOSE 4200

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:4200", "wakeonlanservice.app:app"]