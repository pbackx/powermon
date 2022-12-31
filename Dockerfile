# TODO:
# - Document development process (start both back- and frontend)
# - Fix Flask warning: WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.

ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN \
  apk add --no-cache \
    python3 py3-pip nginx \
  && mkdir -p /run/nginx

COPY ingress.conf /etc/nginx/http.d/
RUN mkdir /frontend
COPY powermon-frontend/build /frontend

COPY run.sh /
RUN chmod a+x /run.sh

# Python
RUN mkdir /backend
COPY powermon-backend /backend
RUN cd /backend && pip3 install --no-cache-dir -r requirements.txt

CMD [ "/run.sh" ]