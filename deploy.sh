# Variables
BLUE_COMPOSE_FILE=docker-compose-blue.prod.yml
GREEN_COMPOSE_FILE=docker-compose-green.prod.yml
VERSION_FILE=current_version.txt

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
    NEW_NGINX_CONFIG="nginx-green.conf"
    OLD_NGINX_CONFIG="nginx-blue.conf"
    NEW_PORT=8001
    OLD_PORT=8000
else
    NEW_VERSION="blue"
    NEW_COMPOSE_FILE=$BLUE_COMPOSE_FILE
    OLD_COMPOSE_FILE=$GREEN_COMPOSE_FILE
    NEW_SERVICE="backend_blue"
    OLD_SERVICE="backend_green"
    NEW_NGINX_CONFIG="nginx-blue.conf"
    OLD_NGINX_CONFIG="nginx-green.conf"
    NEW_PORT=8000
    OLD_PORT=8001
fi

# Build and deploy new version
echo "Building and deploying $NEW_SERVICE..."
docker-compose -f $NEW_COMPOSE_FILE build $NEW_SERVICE
docker-compose -f $NEW_COMPOSE_FILE up -d $NEW_SERVICE

# Copy new Nginx configuration to container and reload
echo "Reloading Nginx configuration..."
docker-compose -f $NEW_COMPOSE_FILE down nginx
docker-compose -f $NEW_COMPOSE_FILE up -d nginx

docker-compose -f $NEW_COMPOSE_FILE exec nginx nginx -s reload

# Stop old version
echo "Stopping old version $OLD_SERVICE..."
docker-compose -f $OLD_COMPOSE_FILE stop $OLD_SERVICE

# Update version file
echo "Updating version file..."
echo $NEW_VERSION > $VERSION_FILE

echo "Deployment completed successfully!"
