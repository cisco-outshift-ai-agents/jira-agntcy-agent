# Use the hardened Python image from Cisco
FROM containers.cisco.com/eti-sre/sre-python-docker:v3.11.9-hardened-debian-12

ARG DEBIAN_FRONTEND=noninteractive
ARG BUILD_VERSION=""
RUN apt-get update && \
  apt-get -y upgrade && \
  apt-get install -yq --no-install-recommends ca-certificates

RUN rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

# Add user app
RUN useradd -u 1001 app

# Create the app directory and set permissions to app
RUN mkdir /home/app/ && chown -R app:app /home/app

WORKDIR /home/app

# Run the application as user app
USER app

# Copy the dependencies file to the working directory
COPY --chown=app:app requirements.txt .

# Install dependencies
RUN --mount=type=secret,id=PIP_EXTRA_INDEX_URL,uid=1001 export PIP_EXTRA_INDEX_URL=$(cat /run/secrets/PIP_EXTRA_INDEX_URL) \
    && pip3 install --no-cache-dir --user -r requirements.txt

# Copy the content of the local app directory to the working directory
COPY --chown=app:app . .

ENV BUILD_VERSION=${BUILD_VERSION}

RUN pwd
RUN mkdir tmpdata
RUN chmod 644 tmpdata

# Command to run on container start
CMD ["python3", "app/main.py"]