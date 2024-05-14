FROM postgres:15
ENV POSTGRES_PASSWORD=${DB_PASSWORD}
EXPOSE 5432
COPY 00_init.sql /docker-entrypoint-initdb.d

CMD ["postgres"]