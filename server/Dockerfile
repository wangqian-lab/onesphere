FROM docker.pkg.github.com/masami10/odoo_crack_docker/oneshare_odoo:14

USER root

#onesphere addons requirements
COPY ./requirements.txt /

RUN pip3 install --upgrade pip \
    && pip3 install -r /requirements.txt \
    && curl https://dl.min.io/client/mc/release/linux-amd64/mc -o /usr/bin/mc \
    && chmod +x /usr/bin/mc \
    && mc alias set onesphere http://172.17.0.1:9000 minio minio123

COPY ./onesphere /mnt/extra-addons/
COPY ./oneshare_base /mnt/extra-addons/

# oneshare base requirements
RUN pip3 install -r /mnt/extra-addons/requirements.txt \
    && rm -f /requirements.txt \
    && rm -f /mnt/extra-addons/requirements.txt

USER odoo