# Get the local IP address dynamically
LOCAL_IP := $(shell hostname -I | awk '{print $$1}')
SSL_DIR := nginx/ssl

# Default target: Generate SSL certificates and start Docker Compose
all: certs build up

# Build Docker images
build:
	@if [ ! -f .env ]; then \
		echo ".env file not found! Exiting."; \
		exit 1; \
	fi
	docker-compose -f ./docker-compose.yml --env-file .env build

# Start Docker containers using the .env file
up:
	@if [ ! -f .env ]; then \
		echo ".env file not found! Exiting."; \
		exit 1; \
	fi
	docker-compose -f ./docker-compose.yml --env-file .env up -d

# Stop Docker containers
down:
	docker-compose down

# Stop containers and prune unused Docker resources
clean: down
	docker system prune -f
	docker volume prune -f

# Full cleanup: Remove all Docker resources (containers, images, volumes, networks)
fclean: clean
	docker-compose down --volumes
	docker rm -f $(shell docker ps -aq)
	docker rmi -f $(shell docker images -aq)
	docker volume rm $(shell docker volume ls -q)
	docker network rm $(shell docker network ls -q)
	docker system prune -a --volumes -f

# Rebuild the project (clean, build, and start Docker containers)
re: clean build up

# Generate SSL certificates dynamically based on the machine's local IP
certs:
	@mkdir -p $(SSL_DIR)
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout $(SSL_DIR)/selfsigned.key \
		-out $(SSL_DIR)/selfsigned.crt \
		-subj "/C=US/ST=State/L=City/O=Company/CN=$(LOCAL_IP)"
	@echo "SSL certificates generated for IP: $(LOCAL_IP)"

# Declare phony targets to prevent conflicts with real files
.PHONY: all build up down clean fclean re certs
