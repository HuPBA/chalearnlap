FROM python:3.10-alpine

# Create the working folder
RUN mkdir /code/
WORKDIR /code/

# Add requirements
ADD requirements.txt requirements.txt

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step.
RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
            g++ \
            gcc \
            make \
            libc-dev \
            musl-dev \
            linux-headers \
            pcre-dev \
            postgresql-dev \
	        libxml2-dev \
	        libxslt-dev \
            mariadb-dev \
            libffi-dev \
	        jpeg-dev \
	        freetype-dev \
            zlib-dev \
            git \
            python3-dev \
    && python3 -m venv /venv \
    && /venv/bin/pip install -U pip \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "/venv/bin/pip install --no-cache-dir wheel uwsgi mysqlclient psycopg2 -r requirements.txt --upgrade" \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive /venv \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk del .build-deps

# Install production dependencies
RUN set -ex \
    && apk add --no-cache \
            postgresql-client \
            bash \
            vim \
            gcc \
            libressl-dev \
            freetype \
            jpeg \
            libxml2 \
            libxslt \
            nginx \
            supervisor \
            uwsgi \
            uwsgi-python3 \
            mariadb-connector-c

# Copy and prepare the entrypoint script for front-end
ADD docker/docker-entrypoint.sh /bin
RUN dos2unix /bin/docker-entrypoint.sh && chmod +x /bin/docker-entrypoint.sh

# uWSGI will listen on this port
EXPOSE 5000

# Add any custom, static environment variables needed by Django or your settings file here:
ENV DJANGO_SETTINGS_MODULE=chalearnlap.settings
ENV DJANGO_SETTINGS_ENV=Production

# Copy the code
ADD src/chalearnlap /code/chalearnlap
RUN cp /code/chalearnlap/manage.py /code/manage.py

# Create a user and group for uWSGI and Celery
RUN addgroup -g 2000 -S web_group && \
    adduser -u 1000 -S web_user -G web_group

# Give permisions to root folder for this user
RUN chown -R web_user:web_group /code

# Call collectstatic (customize the following line with the minimal environment variables needed for manage.py to run):
RUN DEBUG=1 /venv/bin/python manage.py collectstatic --noinput

# Copy the Nginx global conf
COPY docker/nginx.conf /etc/nginx/
# Copy the Flask Nginx site conf
COPY docker/django-site-nginx.conf /etc/nginx/conf.d/
# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
COPY docker/uwsgi.ini /etc/uwsgi/
# Custom Supervisord config
COPY docker/supervisord.conf /etc/supervisord.conf

CMD ["/usr/bin/supervisord"]
ENTRYPOINT ["docker-entrypoint.sh"]
