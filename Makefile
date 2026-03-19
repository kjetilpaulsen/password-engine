APP_NAME := password_engine

.PHONY: docker-init docker-up docker-down

docker-init:
	APP_NAME=$(APP_NAME) ./scripts/init_docker_dirs.sh

docker-up: docker-init
	docker compose up

docker-down:
	docker compose down
