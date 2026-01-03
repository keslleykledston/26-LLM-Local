# Multi-stage build for optimized caching
FROM node:20-alpine as deps

WORKDIR /app

# Copy package files for dependency installation
COPY package*.json ./

# Install dependencies (use npm install if no lockfile exists)
RUN npm install


# Development stage
FROM node:20-alpine

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy package files
COPY package*.json ./

# Copy app files
COPY . .

# Non-root user for security (use existing node user in alpine)
RUN chown -R node:node /app
USER node

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Run in development mode
CMD ["npm", "run", "dev"]
