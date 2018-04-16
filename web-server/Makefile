brun:
	docker build -t pskreter/web-server:latest .
	docker run --rm -p 8000:8000  pskreter/web-server:latest

build: 
	docker build -t pskreter/web-server:latest .

push:
	docker push pskreter/web-server:latest

run:
	docker run --rm -p 8000:8000  pskreter/web-server:latest

dev:
	docker run -it --rm -p 8000:8000 -v ${PWD}:/app pskreter/web-server:latest /bin/bash