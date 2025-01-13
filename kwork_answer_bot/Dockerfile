# Use the official Python image from the Docker Hub
FROM python:3.10.6

# Install ca-certificates
RUN apt-get update && apt-get install -y ca-certificates

# Set the working directory
WORKDIR /app

# Copy the requirements file and dependecies
COPY pykwork-master.zip .
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt && pip install --upgrade websockets

# Copy the rest of the application code
COPY . .

# Set the entrypoint
CMD ["python", "main.py"]