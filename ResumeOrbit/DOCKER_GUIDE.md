# 🐳 Docker Run Guide

Learn how to run ResumeOrbit using Docker and Docker Compose. This is the easiest way to get the entire application (Python Backend, Node.js Backend, and Frontend) running with a single command.

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your system:
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (for Windows/Mac/Linux)
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

## 🚀 Quick Start

To start the entire application, run the following command from the project root:

```bash
docker-compose up --build
```

This will:
1. Build the Docker images for all three services.
2. Start the containers.
3. Link them together in a secure network.

## 📍 Accessing the Application

Once the services are up and running, you can access them at the following URLs:

- **Frontend**: [http://localhost:8000](http://localhost:8000)
- **Node.js Backend**: [http://localhost:3001](http://localhost:3001)
- **Python Backend**: [http://localhost:5000](http://localhost:5000)

## 🛠️ Common Commands

### Stopping the Application
To stop the services and remove the containers:
```bash
docker-compose down
```

### Running in Background
To run the services in the background (detached mode):
```bash
docker-compose up -d
```

### Viewing Logs
To see the logs from all services:
```bash
docker-compose logs -f
```

### Rebuilding a Single Service
If you've only made changes to one part of the app (e.g., the backend):
```bash
docker-compose up --build python-backend
```

## 📂 Data and Persistence

- **Resume Uploads**: Files uploaded to the Python backend are stored in `./backend/uploads`. This is mapped to a volume so your files persist even if the container is restarted.
- **Database**: The SQLite database for the Node.js backend is stored in `./resume-builder-js/data`. This is also mapped to a volume for persistence.

## 🐛 Troubleshooting

- **Port Conflict**: If you get an error saying a port is already in use, make sure you don't have the application running locally (outside of Docker).
- **Network Issues**: If the services cannot talk to each other, ensure Docker is running and you haven't modified the `networks` configuration in `docker-compose.yml`.
