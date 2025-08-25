FROM node:lts

RUN npm install -g npm

RUN mkdir -p /src

WORKDIR /src

COPY ./package.json ./package.json
COPY ./package.json ./package.json

RUN npm install

VOLUME [ "/src/node_modules" ]

COPY . . 

ENTRYPOINT [ "npm", "run", "serve" ]
