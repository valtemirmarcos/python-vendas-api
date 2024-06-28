#!/bin/bash

# Load environment variables from .env file
set -a
source .env
set +a

DB_NAME=$MYSQL_DATABASE
DB_USER=$MYSQL_USER
DB_PASSWORD=$MYSQL_PASSWORD
DB_HOST=$DB_HOST

MYSQL_CMD="mysql -u $DB_USER -p$DB_PASSWORD -h $DB_HOST"

echo "Checking if database $DB_NAME exists..."

# Verifica se o banco de dados existe
RESULT=$(echo "SHOW DATABASES LIKE '$DB_NAME'" | $MYSQL_CMD)

if [ -z "$RESULT" ]; then
    echo "Database $DB_NAME does not exist. Creating..."
    # Cria o banco de dados
    echo "CREATE DATABASE $DB_NAME" | $MYSQL_CMD
    echo "Database $DB_NAME created."

    # Concede todas as permissões ao usuário 'root' para o banco de dados
    echo "Granting privileges to user 'root'..."
    echo "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD';" | $MYSQL_CMD
    echo "FLUSH PRIVILEGES;" | $MYSQL_CMD
    echo "Privileges granted."
else
    echo "Database $DB_NAME already exists."
fi

echo "Running migrations..."
flask db migrate
flask db upgrade
echo "Migrations completed."
