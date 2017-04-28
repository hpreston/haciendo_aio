FROM python:3.5-alpine
EXPOSE 80

# Install basic utilities
RUN apk add -U \
        ca-certificates \
  && rm -rf /var/cache/apk/* \
  && pip install --no-cache-dir \
          setuptools \
          wheel

# Create application directories
RUN mkdir /app \
  && mkdir /app/static \
  && mkdir /app/templates

# Prep Required Environment Variables
# These are default placeholders but should be overridden
# when running the container
ENV API_SERVER="http://localhost:5000"

# Copy needed application requirements file into image
ADD requirements.txt /app

# Install Python requirements
RUN pip install -r /app/requirements.txt

# Copy the web templates and resources into the image
COPY static /app/static
COPY templates /app/templates

# Copy application code into image
ADD haciendo_web.py /app

# Run the application
CMD cd /app && python haciendo_web.py -p 80 -a ${API_SERVER}/api/score

