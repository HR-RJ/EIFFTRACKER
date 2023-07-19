# Use an official Python runtime as a parent image
FROM python:3.11.4-alpine3.17

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container

# Define environment variable

# Run app.py when the container launches
CMD ["python", "main.py"]
