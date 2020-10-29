ARG VERSION=0.3.1
ARG JAR=JMusicBot-$VERSION.jar

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
CMD java -Dnogui=true -jar ../${JAR}
