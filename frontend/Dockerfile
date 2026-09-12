# ============================================================
# Stage 1: build — run npm build in Node.js environment
# ============================================================
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

# ============================================================
# Stage 2: runtime — nginx:alpine serving static files
# Result: ~25 MB image (no Node.js, npm, or TS source in production)
# ============================================================
FROM nginx:alpine AS runtime

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy built static files
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx config is mounted from the nginx service — this container
# serves the static files directly and forwards /api to backend
COPY nginx-spa.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
