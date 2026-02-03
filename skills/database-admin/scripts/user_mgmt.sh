#!/bin/bash
# user_mgmt.sh - Manage database users

ACTION=$1
USERNAME=$2
DB_NAME=$3

if [ -z "$ACTION" ] || [ -z "$USERNAME" ]; then
    echo "Usage: $0 [create|drop|grant] [username] [database_name]"
    exit 1
fi

if [ "$ACTION" == "create" ]; then
    read -s -p "Enter password for $USERNAME: " PASSWORD
    echo
    psql -c "CREATE USER \"$USERNAME\" WITH PASSWORD '$PASSWORD';"
    echo "User $USERNAME created."
elif [ "$ACTION" == "drop" ]; then
    psql -c "DROP USER \"$USERNAME\";"
    echo "User $USERNAME dropped."
elif [ "$ACTION" == "grant" ]; then
    if [ -z "$DB_NAME" ]; then
        echo "Database name required for grant."
        exit 1
    fi
    psql "$DB_NAME" -c "GRANT ALL PRIVILEGES ON DATABASE \"$DB_NAME\" TO \"$USERNAME\";"
    psql "$DB_NAME" -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \"$USERNAME\";"
    psql "$DB_NAME" -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO \"$USERNAME\";"
    echo "Permissions granted to $USERNAME on $DB_NAME."
else
    echo "Invalid action. Use 'create', 'drop', or 'grant'."
    exit 1
fi
