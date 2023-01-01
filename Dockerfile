ARG BUILD_FROM
FROM $BUILD_FROM

RUN \
  apk add --no-cache \
    python3 py3-pip nginx \
  && mkdir -p /run/nginx

COPY ingress.conf /etc/nginx/http.d/

WORKDIR /frontend
COPY powermon-frontend/build /frontend

WORKDIR /backend
COPY powermon-backend /backend
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install waitress==2.1.2

WORKDIR /
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]