#!/bin/bash

# Variables
BLUE_COMPOSE_FILE=docker-compose-blue.prod.yml
GREEN_COMPOSE_FILE=docker-compose-green.prod.yml
NGINX_COMPOSE_FILE=docker-compose-nginx.yml
VERSION_FILE=current_version.txt
NGINX_CONF_FILE=nginx.conf

if [ -f $VERSION_FILE ]; then
    CURRENT_VERSION=$(cat $VERSION_FILE)
else
    echo "Error: $VERSION_FILE not found!"
    exit 1
fi

# Determine new version
if [ "$CURRENT_VERSION" == "blue" ]; then
    NEW_VERSION="green"
    NEW_COMPOSE_FILE=$GREEN_COMPOSE_FILE
    OLD_COMPOSE_FILE=$BLUE_COMPOSE_FILE
    NEW_SERVICE="backend_green"
    OLD_SERVICE="backend_blue"
    NEW_PORT=8001
    OLD_PORT=8000
else
    NEW_VERSION="blue"
    NEW_COMPOSE_FILE=$BLUE_COMPOSE_FILE
    OLD_COMPOSE_FILE=$GREEN_COMPOSE_FILE
    NEW_SERVICE="backend_blue"
    OLD_SERVICE="backend_green"
    NEW_PORT=8000
    OLD_PORT=8001
fi

# Build and deploy new version
echo "Building and deploying $NEW_SERVICE..."
docker-compose -f $NEW_COMPOSE_FILE build $NEW_SERVICE
docker-compose -f $NEW_COMPOSE_FILE up -d $NEW_SERVICE

# Verify if new service is up and running
echo "Verifying $NEW_SERVICE..."
until docker-compose -f $NEW_COMPOSE_FILE exec $NEW_SERVICE curl -s http://localhost:$NEW_PORT >/dev/null; do
    echo "$NEW_SERVICE is not yet running. Retrying..."
    sleep 5
done

# Update Nginx configuration
echo "Updating Nginx configuration..."
if [ "$NEW_VERSION" == "green" ]; then
    sed -i 's/server backend_blue:8000;/server backend_green:8001;/g' $NGINX_CONF_FILE
else
    sed -i 's/server backend_green:8001;/server backend_blue:8000;/g' $NGINX_CONF_FILE
fi

# Restart Nginx container to apply new configuration
echo "Restarting Nginx container..."
docker-compose -f $NGINX_COMPOSE_FILE restart nginx

# Verify if new Nginx is correctly running
echo "Verifying new Nginx..."
until docker-compose -f $NGINX_COMPOSE_FILE exec nginx curl -s https://rumz.site >/dev/null; do
    echo "New Nginx is not yet responding. Retrying..."
    sleep 5
done

# Stop old version
echo "Stopping old version $OLD_SERVICE..."
docker-compose -f $OLD_COMPOSE_FILE stop $OLD_SERVICE

echo "Removing old data..."
docker system prune -a --volumes -f

# Update version file
echo "Updating version file..."
echo $NEW_VERSION > $VERSION_FILE

echo "Deployment completed successfully!"
