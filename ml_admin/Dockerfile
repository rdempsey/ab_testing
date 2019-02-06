FROM python:3.7.2-alpine
MAINTAINER Robert Dempsey <robertonrails@gmail.com>

ARG BUILD_NUMBER=0
ENV BUILD_NUMBER $BUILD_NUMBER

# Install Linux dependencies
RUN apk --no-cache add musl-dev linux-headers g++

# Install Python requirements
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# Run the container
CMD ["gunicorn", "-b", "0.0.0.0:5001", "admin:app", "--workers 9", "--threads 2"]