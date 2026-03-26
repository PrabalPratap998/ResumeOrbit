# Node.js Backend Dockerfile
FROM node:18-slim

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install --production

# Copy the rest of the application code
COPY . .

# Create data directory for SQLite
RUN mkdir -p data

# Expose port 3001
EXPOSE 3001

# Set default environment variables
ENV PORT=3001
ENV PYTHON_API_URL=http://python-backend:5000

# Command to run the application
CMD ["node", "server.js"]
