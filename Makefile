DOCKER_NAME=meteotoni
VERSION=0.0.1
DOCKER_NAME_FULL=$(DOCKER_NAME):$(VERSION)

build:
	docker build -t $(DOCKER_NAME_FULL) .

run:
	docker-compose -f docker-compose.yml up -d
