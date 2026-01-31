FROM nginx:alpine

COPY ./nginx/ /etc/nginx/
COPY ./www/dist/assets/ /var/www/app/assets/
COPY ./www/dist/index.html /var/www/app/
COPY ./www/dist/icon.png /var/www/app/
COPY ./www/dist/fonts/ /var/www/app/fonts/
COPY ./www/dist/img/ /var/www/app/img/

EXPOSE 80
EXPOSE 443

