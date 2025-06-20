# Use python:slim as the base image
FROM python:slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set up a working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock* ./

# Copy the rest of the application code
COPY . .

# Install dependencies using Poetry
RUN poetry install --no-root --only main --no-interaction --no-ansi

# Expose port 8000
EXPOSE 8000

# Set the command to run Gunicorn using Poetry
CMD ["poetry", "run", "gunicorn", "boardgame_timer.wsgi:application", "--bind", "0.0.0.0:8000"]
