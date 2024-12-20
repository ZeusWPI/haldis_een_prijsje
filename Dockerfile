# Use an official Python runtime as the base image
FROM python:3.12.4-alpine

# Set the working directory in the container
WORKDIR /flask-app

# Copy the entire project directory (including requirements.txt) into the container
COPY . /flask-app/

# Install dependencies
RUN pip install -r /flask-app/requirements.txt

# Expose the port Flask will run on
EXPOSE 5000

# Set the entry point to run the Flask app (assuming app.py is located in the root of /flask-app)
CMD ["python", "/flask-app/website/app.py"]
