FROM node:22.0.0-alpine AS cssbuild

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY trojstenid ./trojstenid
COPY tailwind.config.js ./
RUN npm run css-prod
CMD ["npm", "run", "css-dev"]


FROM ghcr.io/trojsten/django-docker:v6

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY --chown=appuser:appuser . /app/
COPY --chown=appuser:appuser --from=cssbuild /app/trojstenid/users/static/app.css /app/trojstenid/users/static/app.css

RUN /app/build.sh
ENV BASE_START=/app/start.sh
