FROM mcr.microsoft.com/devcontainers/universal:2

RUN apt-get update && apt-get install -y --no-install-recommends libsasl2-dev python-dev libldap2-dev libssl-dev

RUN git clone -b 16.0 --depth 1 https://github.com/odoo/odoo.git /odoo

RUN cd /odoo && sed -n -e '/^Depends:/,/^Pre/ s/ python3-\(.*\),/python3-\1/p' debian/control | sudo xargs apt-get install -y && pip install -r requirements.txt

RUN npm install -g rtlcss

RUN cp /odoo/debian/odoo.conf /etc/odoo.conf

RUN sed -i 's/odoo/codespace/g' /etc/odoo.conf

RUN echo "addons_path = /workspaces/dumblodoo,/odoo/addons" >> /etc/odoo.conf

# Create the file repository configuration:
RUN sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

# Import the repository signing key:
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Update the package lists:
RUN sudo apt-get update

# Install the latest version of PostgreSQL.
# If you want a specific version, use 'postgresql-12' or similar instead of 'postgresql':
RUN apt-get -y install postgresql

CMD service postgresql start && sudo -u postgres createuser -s codespace
