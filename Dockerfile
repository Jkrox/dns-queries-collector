FROM python:3.12-slim-bookworm

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

ENTRYPOINT [ "python3", "main.py", "queries.log"]