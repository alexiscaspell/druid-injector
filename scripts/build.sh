source ./scripts/ambiente.sh

docker build \
--build-arg TAG=$VERSION \
-t $DOCKER_HUB_REPO:$VERSION .
