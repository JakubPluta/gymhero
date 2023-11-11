FROM postgres:16-alpine

ENV POSTGRES_USER=gymhero
ENV POSTGRES_PASSWORD=p4ssw0rd
ENV POSTGRES_DB=workout

COPY ./init.sql /docker-entrypoint-initdb.d/init.sql