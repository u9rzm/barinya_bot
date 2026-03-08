FROM nginx:alpine
COPY ./nginx/ /etc/nginx/
COPY ./www/v1/dist/ /var/www/v1/
COPY ./www/v2/dist/ /var/www/v2/
# COPY ./storage/ /var/www/storage/
EXPOSE 80
EXPOSE 443

