1. Install postgres:
sudo apt update
sudo apt install libpq-dev python3-dev build-essential
sudo apt install postgresql postgresql-contrib -y
sudo apt install postgresql-doc
sudo systemctl status postgresql
sudo systemctl enable postgresql

sudo -u postgres createuser -s bmesesan
createdb mydb


2. How to create local DB to be used:
sudo -i -u postgres
psql
CREATE USER allocation WITH PASSWORD 'abc123';
CREATE DATABASE allocation;
GRANT ALL PRIVILEGES ON DATABASE allocation TO allocation;
ALTER DATABASE allocation OWNER TO allocation;
exit
psql -U allocation -d allocation -h localhost -p 5432 -W