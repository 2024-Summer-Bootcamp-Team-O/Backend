# Variables
BLUE_COMPOSE_FILE=docker-compose-blue.prod.yml
GREEN_COMPOSE_FILE=docker-compose-green.prod.yml
NGINX_CONFIG_FILE=nginx.conf
VERSION_FILE=current_version.txt

# Read current version from the file
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
docker-compose -f $NEW_COMPOSE_FILE build $NEW_SERVICE
docker-compose -f $NEW_COMPOSE_FILE up -d $NEW_SERVICE

# Update Nginx configuration
sed -i "s|proxy_pass http://.*:800[0-1];|proxy_pass http://$NEW_SERVICE:$NEW_PORT;|g" $NGINX_CONFIG_FILE

# Reload Nginx to apply new configuration
docker-compose -f $NEW_COMPOSE_FILE exec nginx nginx -s reload

# Stop old version
docker-compose -f $OLD_COMPOSE_FILE stop $OLD_SERVICE

# Update version file
echo $NEW_VERSION > $VERSION_FILE
