FROM python:3.5-alpine
EXPOSE 5000

# Install basic utilities
RUN apk add -U \
        ca-certificates \
  && rm -rf /var/cache/apk/* \
  && pip install --no-cache-dir \
          setuptools \
          wheel

# Create application directories
RUN mkdir /app

# Prep Required Environment Variables
# These are default placeholders but should be overridden
# when running the container
ENV SMS_SERVER="http://localhost:5001"

# Copy needed application requirements file into image
ADD requirements.txt /app

# Install Python requirements
RUN pip install -r /app/requirements.txt

# Copy application code into image
ADD haciendo_api.py /app

# Run the application
CMD cd /app && python haciendo_api.py -p 5000 -t ${SMS_SERVER}/score

