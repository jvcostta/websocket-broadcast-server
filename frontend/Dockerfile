# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Instala dependências
COPY package*.json ./
RUN npm ci

# Copia código e faz build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copia arquivos buildados
COPY --from=builder /app/dist /usr/share/nginx/html

# Copia configuração customizada do nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
