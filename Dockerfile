# Dockerfile to use with the statssaver script
# Uses an alpine image to reduce image size
# On top, install python3 (current version), pip3, and request
# Once the package is available in pypi, it will be installed
# Beyond that, the container can be used with any
# script that only requires requests

# Current latest release of alpine at January 8th 2025
FROM alpine:3.21.1

# Installing python and pip
RUN apk add --no-cache git python3 py3-pip

RUN git clone https://github.com/ConesaLab/Github-stats-saver.git && cd Github-stats-saver && pip install --break-system-packages .
