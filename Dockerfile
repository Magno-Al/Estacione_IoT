FROM node:22-alpine AS base

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install --only=production

COPY . .

EXPOSE ${PORT:-3000}

CMD [ "npm", "start" ]