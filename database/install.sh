DB_USER="wmnlab"
DB_PASSWD="facantu249"

sudo apt-get update
echo "mysql-server mysql-server/root_password password $DB_PASSWD" | sudo debconf-set-selections
echo "mysql-server mysql-server/root_password_again password $DB_PASSWD" | sudo debconf-set-selections
sudo apt-get install -y mysql-server
sudo apt-get install -y mysql-client

mysql -u root -p"$DB_PASSWD" -e "SET @DB_USER='$DB_USER', @DB_PASSWD='$DB_PASSWD'; SOURCE create_db.sql;"
