FROM python:2.7-alpine
EXPOSE 5001

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
#   ** TROPO_PREFIX can be left as 1419 unless you want to change
ENV TROPO_USER="tuser" \
    TROPO_PASS="tpass" \
    TROPO_PREFIX="1419" \
    TROPO_URL="http://"

# Copy needed application requirements file into image
ADD requirements.txt /app

# Install Python requirements
RUN pip install -r /app/requirements.txt

# Copy application code into image
ADD haciendo_sms.py /app

# Run the application
CMD cd /app && python haciendo_sms.py \
                        -p 5001 \
                        -t ${TROPO_USER} \
                        -w ${TROPO_PASS} \
                        --tropoprefix ${TROPO_PREFIX} \
                        --tropourl ${TROPO_URL}
