#!/bin/bash
set -e

# Function to create database and user if they don't exist
create_db_and_user() {
    local db=$1
    local user=$2
    local password=$3

    # Create user if not exists
    echo "Creating user $user..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        DO
        \$do\$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$user') THEN
                CREATE USER $user WITH PASSWORD '$password';
            END IF;
        END
        \$do\$;
EOSQL

    # Create database if not exists
    echo "Creating database $db..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        SELECT 'CREATE DATABASE $db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$db')\gexec
        GRANT ALL PRIVILEGES ON DATABASE $db TO $user;
EOSQL

    # Connect to the database and set ownership
    echo "Setting ownership and permissions..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$db" <<-EOSQL
        ALTER SCHEMA public OWNER TO $user;
        GRANT ALL ON SCHEMA public TO $user;
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $user;
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $user;
EOSQL

    echo "Database $db and user $user setup completed successfully."
}

# Create production database
create_db_and_user "locavox" "locavox_user" "locavox_pass"

# Create test database
create_db_and_user "locavox_test" "locavox_test" "locavox_test"

echo "All databases created successfully."
