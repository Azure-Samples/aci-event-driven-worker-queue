build:
	docker build -t pskreter/worker-container:latest .

push:
	docker push pskreter/worker-container:latest

test:
	docker run --rm -e CONTAINER_NAME=test -e MESSAGE=test1 -e DATABASE_URI=${MONGO_URI} --name worker-go pskreter/worker-container

run:
	docker run --rm --name worker-containe pskreter/worker-container:latest