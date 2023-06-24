FROM nginx:stable

RUN apt-get update && apt-get install -y openssl

WORKDIR /etc/nginx/ssl

RUN openssl genpkey -algorithm RSA -out ssl.key
RUN openssl req -new -key ssl.key -x509 -days 365 -out ssl.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=example.com"

COPY default.conf /etc/nginx
COPY default.conf /etc/nginx/conf.d

EXPOSE 80
