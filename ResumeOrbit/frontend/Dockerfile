# Frontend Dockerfile
FROM nginx:alpine

# Copy static files to Nginx html directory
COPY . /usr/share/nginx/html

# Use custom nginx config with API reverse proxies
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Command to run Nginx
CMD ["nginx", "-g", "daemon off;"]
