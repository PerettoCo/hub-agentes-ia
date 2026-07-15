FROM nginx:alpine

RUN rm -f /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/nginx.conf
COPY run.sh /run.sh

RUN chmod +x /run.sh

EXPOSE 80

CMD ["/run.sh"]
