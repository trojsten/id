FROM node:22.0.0-alpine AS cssbuild

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY trojstenid ./trojstenid
COPY tailwind.config.js ./
RUN npm run css-prod
CMD ["npm", "run", "css-dev"]


FROM ghcr.io/trojsten/django-docker:v4

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY . /app/
COPY --from=cssbuild /app/trojstenid/users/static/app.css /app/trojstenid/users/static/app.css

ENV BASE_START=/app/start.sh
