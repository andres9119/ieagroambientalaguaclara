# Despliegue - I.E Agroambiental Agua Clara
# IONOS VPS S - Ubuntu

# 1. Sistema
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib certbot python3-certbot-nginx

# 2. PostgreSQL
sudo -u postgres psql -c "CREATE USER colegio_user WITH PASSWORD 'contraseña_segura';"
sudo -u postgres psql -c "CREATE DATABASE colegio_db OWNER colegio_user;"
sudo -u postgres psql -c "ALTER USER colegio_user CREATEDB;"

# 3. Clonar/Copiar proyecto
sudo mkdir -p /var/www/colegio_web
# Copiar archivos del proyecto a /var/www/colegio_web/

# 4. Entorno virtual y dependencias
cd /var/www/colegio_web
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Variables de entorno
cp .env.example .env
nano .env  # <-- EDITAR con valores reales

# 6. Migraciones y estáticos
cd /var/www/colegio_web
source env/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# 7. Directorios para logs y socket
sudo mkdir -p /var/www/colegio_web/run /var/www/colegio_web/logs
sudo chown -R www-data:www-data /var/www/colegio_web

# 8. Gunicorn como servicio
sudo cp deploy/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn

# 9. Nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/colegio
sudo ln -sf /etc/nginx/sites-available/colegio /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 10. SSL con Let's Encrypt
sudo certbot --nginx -d ieagroambientalaguaclara.com -d www.ieagroambientalaguaclara.com

# 11. Verificar
sudo systemctl status gunicorn
sudo systemctl status nginx
