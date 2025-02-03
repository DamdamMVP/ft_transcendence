# Base Node.js image
FROM node:20-alpine

# Definition of the working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port for Vite (default 5173)
EXPOSE 5173

# Command to launch development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]