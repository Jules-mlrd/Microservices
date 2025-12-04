terraform {
    required_providers {
        docker = {
            source = "kreuzwerker/docker"
            version = " ~> 3.0"
        }
    }
}
provider "docker" {}
variable "catalog_port" {
    type = number
    description = "Port exposé pour le service catalog"
    default = 8081
}
variable "cart_port" {
    type = number
    description = "Port exposé pour le service cart"
    default = 8082
}
resource "docker_network" "ecommerce" {
    name = "ecommerce-net"
}
resource "docker_image" "service" {
    name = "nginxdemos/hello:latest"
    keep_locally = true
}
# Conteneur pour le service catalog
resource "docker_container" "catalog" {
    name = "catalog-service"
    image = docker_image.service.image_id
    networks_advanced {
        name = docker_network.ecommerce.name
    }
    ports {
        internal = 80
        external = var.catalog_port
    }
    env = [
        "SERVICE_NAME=catalog",
        "ENVIRONMENT=dev"
    ]
}

# Conteneur pour le service cart
resource "docker_container" "cart" {
    name = "cart-service"
    image = docker_image.service.image_id
    networks_advanced {
        name = docker_network.ecommerce.name
    }
    ports {
        internal = 80
        external = var.cart_port
    }
    env = [
        "SERVICE_NAME=cart",
        "ENVIRONMENT=dev"
    ]
}

output "catalog_url" {
    value = "http://localhost:${var.catalog_port}"
}

output "cart_url" {
    value = "http://localhost:${var.cart_port}"
}

