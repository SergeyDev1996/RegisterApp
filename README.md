FastAPI User Management Project
This project provides a basic user management and verification system using FastAPI. It includes endpoints for user registration, login, and password reset functionality, along with email verification.

Requirements
Docker (for containerized deployment)
Python 3.8 or higher (for local development)

## 1. Running the Application Using Docker
The project is containerized using Docker. You can build and run the Docker container by following these steps:
Run the following command in the root directory of the project to run the docker-compose:
```
docker-compose up --build
```

## 2. Environment Variables
The application uses the following environment variables. You can define them in a .env file in the root directory

## 2. Accessing the API
Once the container is running, the FastAPI application will be available at:

API Endpoint: http://localhost:8000/api
Swagger Documentation: http://localhost:8000/api/docs
You can use the Swagger UI to interact with the API and test the endpoints.

## 3. API Documentation
FastAPI automatically generates documentation for the API. You can access it at the following URL after starting the server:

Swagger UI: http://localhost:8000/api/docs
ReDoc UI: http://localhost:8000/api/redoc