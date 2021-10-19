FROM docker.pkg.github.com/masami10/odoo_crack_docker/oneshare_odoo:14

USER root

#onesphere addons requirements
COPY ./requirements.txt /

RUN pip3 install --upgrade pip \
    && pip3 install -r /requirements.txt

COPY ./onesphere /mnt/extra-addons/
COPY ./oneshare_base /mnt/extra-addons/

# oneshare base requirements
RUN pip3 install -r /mnt/extra-addons/requirements.txt \
    && rm -f /requirements.txt \
    && rm -f /mnt/extra-addons/requirements.txt

USER odoo