FROM python:3.10-slim

# Set unbuffered output for python
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=djangotest.settings

# Create app directory
WORKDIR /app

# Install app dependencies
COPY requirements.txt .
RUN pip install --upgrade pip

RUN pip install -r requirements.txt


# Add wait-for-it script
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Bundle app source
COPY . .

# Ensure django.sh is executable
RUN chmod +x /app/django.sh

# Expose port
EXPOSE 8000

# Entrypoint to run the django.sh file
ENTRYPOINT ["/app/django.sh"]