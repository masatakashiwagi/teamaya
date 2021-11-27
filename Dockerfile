FROM openjdk:8-alpine
LABEL MAINTAINER=masatakashiwagi

ENV EMBULK_VERSION="0.9.23"

RUN apk --update add --virtual build-dependencies \
    curl \
    tzdata \
    coreutils \
    bash \
    && curl --create-dirs -o /embulk/bin/embulk -L "https://dl.embulk.org/embulk-$EMBULK_VERSION.jar" \
    && chmod +x /embulk/bin/embulk \
    && cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && apk del build-dependencies --purge

ENV PATH="$PATH:/embulk/bin"

# Install libc6-compat for Embulk Plugins to use JNI
# cf: https://github.com/jruby/jruby/wiki/JRuby-on-Alpine-Linux
# https://github.com/classmethod/docker-embulk
RUN apk --update add libc6-compat

# Copy Embulk configuration
COPY ./teamaya/data_integration/embulk/task /opt/embulk/task

# Make bundle
WORKDIR /opt/embulk
RUN embulk mkbundle bundle

# Copy Gemfile file
# This is the workaround, because jruby directory is not created
COPY ./teamaya/data_integration/embulk/bundle/Gemfile /opt/embulk/bundle
COPY ./teamaya/data_integration/embulk/bundle/Gemfile.lock /opt/embulk/bundle
WORKDIR /opt/embulk/bundle

# Install Embulk Plugins
RUN embulk bundle
WORKDIR /opt/embulk

ENTRYPOINT []
CMD ["tail", "-f", "/dev/null"]