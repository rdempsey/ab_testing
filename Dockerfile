FROM python:3.7
MAINTAINER Robert Dempsey <robertonrails@gmail.com>

ARG BUILD_NUMBER=0
ENV BUILD_NUMBER $BUILD_NUMBER

# Install Python requirements
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# Start the agent
ENV PYTHONPATH /usr/src/app