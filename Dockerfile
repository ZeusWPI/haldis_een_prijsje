# Use an official Python runtime as the base image
FROM python:3.12.4

RUN apt-get update
RUN apt-get install -y chromium

# Set the working directory in the container
WORKDIR /haldis_prijsje


# Copy the entire project directory (including requirements.txt) into the container
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port Flask will run on
EXPOSE 5000

# Set the entry point to run the Flask app (assuming app.py is located in the root of /flask-app)
CMD ["python", "/haldis_prijsje/website/app.py"]
