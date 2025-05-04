FROM node:23-alpine AS cssbuild

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && \
    pnpm install

COPY trojstenid ./trojstenid
COPY tailwind.config.js ./
RUN pnpm run css-prod
CMD ["pnpm", "run", "css-dev"]


FROM ghcr.io/trojsten/django-docker:v6

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY --chown=appuser:appuser . /app/
COPY --chown=appuser:appuser --from=cssbuild /app/trojstenid/users/static/app.css /app/trojstenid/users/static/app.css

RUN /app/build.sh
ENV BASE_START=/app/start.sh
