ARG VERSION=0.2.9
ARG JAR=JMusicBot-$VERSION-Linux.jar

FROM debian:buster-slim as linux
ARG VERSION
ARG JAR

WORKDIR /binaries
RUN apt-get update && \
    apt-get install -y curl && \
    curl -LOs -C - https://github.com/jagrosh/MusicBot/releases/download/${VERSION}/${JAR}

FROM java:8
ARG VERSION
ARG JAR
ENV JAR ${JAR}

WORKDIR /app
COPY --from=linux /binaries/${JAR} ${JAR}
WORKDIR /app/config
COPY config.txt config.txt
CMD java -Dnogui=true -jar ../${JAR}
