#!/bin/bash

# Генерация самоподписанного SSL сертификата для разработки
# В продакшене используйте Let's Encrypt

mkdir -p /etc/nginx/ssl

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/key.pem \
    -out /etc/nginx/ssl/cert.pem \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=QR Scanner/CN=localhost"

# Генерация DH параметров
openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048

echo "SSL сертификаты сгенерированы"