#!/bin/bash

# Variables
BLUE_COMPOSE_FILE=docker-compose-blue.prod.yml
GREEN_COMPOSE_FILE=docker-compose-green.prod.yml
VERSION_FILE=current_version.txt
NGINX_CONF_FILE=nginx.conf
NGINX_CONF_PATH=/etc/nginx/nginx.conf

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
    NEW_SERVICE="backend-green"
    OLD_SERVICE="backend-blue"
    NEW_PORT=8001
    OLD_PORT=8000
else
    NEW_VERSION="blue"
    NEW_COMPOSE_FILE=$BLUE_COMPOSE_FILE
    OLD_COMPOSE_FILE=$GREEN_COMPOSE_FILE
    NEW_SERVICE="backend-blue"
    OLD_SERVICE="backend-green"
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

echo "Fetching IP address of the new service..."
if [ "$NEW_VERSION" == "green" ]; then
    NEW_SERVICE_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' backend-green)
    OLD_SERVICE_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' backend-blue)
    sudo sed -i "s/server ${OLD_SERVICE_IP}:8000;/server ${NEW_SERVICE_IP}:8001;/g" $NGINX_CONF_PATH
else
    NEW_SERVICE_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' backend-blue)
    OLD_SERVICE_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' backend-green)
    sudo sed -i "s/server ${OLD_SERVICE_IP}:8001;/server ${NEW_SERVICE_IP}:8000;/g" $NGINX_CONF_PATH
fi

echo "Reloading Nginx configuration..."
sudo nginx -s reload

# Stop old version
echo "Stopping old version $OLD_SERVICE..."
docker-compose -f $OLD_COMPOSE_FILE stop $OLD_SERVICE

echo "Removing old data..."
docker system prune -a --volumes -f

# Update version file
echo "Updating version file..."
echo $NEW_VERSION > $VERSION_FILE

echo "Deployment completed successfully!"
