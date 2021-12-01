FROM openjdk:8-alpine
LABEL MAINTAINER=masatakashiwagi

ENV DIGDAG_VERSION="0.9.42"
ENV EMBULK_VERSION="0.9.23"

RUN apk --update add --virtual build-dependencies \
    curl \
    tzdata \
    coreutils \
    bash \
    postgresql-client \
    musl-dev postgresql-dev postgresql-libs \
    && curl --create-dirs -o /bin/digdag -L "https://dl.digdag.io/digdag-${DIGDAG_VERSION}" \
    && curl --create-dirs -o /bin/embulk -L "https://dl.embulk.org/embulk-$EMBULK_VERSION.jar" \
    && chmod +x /bin/digdag \
    && chmod +x /bin/embulk \
    && cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && apk del build-dependencies --purge

ENV PATH="$PATH:/bin"

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

# Set up Digdag Server
COPY ./teamaya/data_integration/digdag /opt/digdag
# ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /bin/wait
# RUN chmod +x /bin/wait
WORKDIR /opt/digdag

# COPY ./teamaya/data_integration/digdag/entrypoint.sh /bin
# RUN chmod +x /bin/entrypoint.sh

CMD ["tail", "-f", "/dev/null"]
# ENTRYPOINT ["sh","/bin/entrypoint.sh","/bin/digdag","server","--config","/opt/digdag/digdag.properties"]

# ENV DB_TYPE=postgresql \
#     DB_USER=digdag \
#     DB_PASSWORD=digdag \
#     DB_HOST=postgresql \
#     DB_PORT=5432 \
#     DB_NAME=digdag

# CMD exec digdag server --bind $SERVER_BIND \
#                        --port $SERVER_PORT \
#                        --config /opt/digdag/server.properties \
#                        --log /var/lib/digdag/logs/server \
#                        --task-log /var/lib/digdag/logs/tasks \
#                        -X database.type=$DB_TYPE \
#                        -X database.user=$DB_USER \
#                        -X database.password=$DB_PASSWORD \
#                        -X database.host=$DB_HOST \
#                        -X database.port=$DB_PORT \
#                        -X database.database=$DB_NAME \
#                        -X database.maximumPoolSize=32