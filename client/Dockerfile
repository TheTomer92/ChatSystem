# Use an official Python runtime as a parent image
FROM python:3-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN python -m pip install -r requirements.txt

# Run client.py when the container launches
CMD ["python", "client.py"]
