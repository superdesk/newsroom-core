# BUILD
FROM node:14

# install client
WORKDIR /opt/client

COPY package.json .
RUN npm install --no-audit --unsafe-perm

COPY . .

CMD ["npm", "run", "start"]