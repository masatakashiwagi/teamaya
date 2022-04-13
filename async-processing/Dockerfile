FROM python:3.8
LABEL MAINTAINER=masatakashiwagi

# Set some environment variables.
# PYTHONUNBUFFERED keeps Python from buffering our standard
# output stream, which means that logs can be delivered to the user quickly.

ENV PYTHONUNBUFFERED=TRUE

# PYTHONDONTWRITEBYTECODE keeps Python from writing the .pyc files which
# are unnecessary in this case.
ENV PYTHONDONTWRITEBYTECODE=TRUE

# DEBIAN_FRONTEND prevent from stoping docker build with tzdata
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt-get install -y --no-install-recommends \
        curl \
        sudo \
        bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.lock /tmp/requirements.lock
RUN python3 -m pip install -U pip && \
    python3 -m pip install -r /tmp/requirements.lock && \
    rm /tmp/requirements.lock && \
    rm -rf /root/.cache

# Timezone jst
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# Locale Japanese
ENV LC_ALL=ja_JP.UTF-8

# Set up the program in the image
ENV PROGRAM_DIR=/opt/program
COPY app $PROGRAM_DIR
WORKDIR $PROGRAM_DIR
ENV PATH="/opt/program:${PATH}"
ENV PYTHONPATH /opt/program/

CMD ["python3"]