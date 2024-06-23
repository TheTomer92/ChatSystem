# Use an official Python runtime as a parent image
FROM python:3-slim

# # Make port 5678 available to the world outside this container
# EXPOSE 5678

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# # Install any needed packages
# RUN pip install requests

# Run client.py when the container launches
CMD ["python", "client.py"]

# CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "client.py"]