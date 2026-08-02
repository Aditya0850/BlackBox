FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Expose the port Vite runs on
EXPOSE 3000

# Run the application in development mode
CMD ["npm", "run", "dev", "--", "--host", "--port", "3000"]