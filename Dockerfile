# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory
WORKDIR /usr/src/app

# Install Poetry
RUN pip install poetry

# Copy the poetry.lock and pyproject.toml files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-dev

# Copy the rest of the application code
COPY . .

# Expose the necessary port (if applicable)
EXPOSE 8080

# Run the application
CMD ["poetry", "run", "python", "bot.py"]
