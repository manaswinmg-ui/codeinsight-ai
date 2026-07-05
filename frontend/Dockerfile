FROM node:20-alpine as builder

WORKDIR /app

COPY package*.json ./

RUN npm ci || npm install

COPY . .

# Run typescript compilation and vite build
RUN npm run build

FROM nginx:stable-alpine as runner

# Copy built assets to default nginx directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration if needed, otherwise rely on default
# Expose port 80 (we port-map to 5173 in docker-compose.yml)
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
