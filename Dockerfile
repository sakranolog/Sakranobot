# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Install supervisord
RUN apt-get update && apt-get install -y supervisor wget


ADD requirements.txt /app
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Add the current directory contents into the container at /app
ADD . /app

# Add supervisord configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports
EXPOSE 5000

# Run supervisord
CMD ["/usr/bin/supervisord"]
