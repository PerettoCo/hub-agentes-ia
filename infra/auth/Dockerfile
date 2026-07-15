FROM node:20-alpine

RUN apk add --no-cache tini

WORKDIR /app

COPY package.json ./
RUN npm install --only=production && npm cache clean --force

COPY server.js .
COPY public/ public/

ENV NODE_ENV=production

EXPOSE 3000

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "server.js"]
