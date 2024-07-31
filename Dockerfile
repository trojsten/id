FROM node:22.0.0-alpine AS cssbuild

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY trojstenid ./trojstenid
COPY tailwind.config.js ./
RUN npm run css-prod
CMD ["npm", "run", "css-dev"]

FROM python:3.12-slim-bookworm
WORKDIR /app
RUN useradd --create-home appuser

ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1
ENV PATH=/home/appuser/.local/bin:$PATH

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt update \
    && apt -y upgrade \
    && apt -y install caddy \
    && apt -y clean \
    && rm -rf /var/lib/apt/lists/*

ARG MULTIRUN_VERSION=1.1.3
ADD https://github.com/nicolas-van/multirun/releases/download/${MULTIRUN_VERSION}/multirun-x86_64-linux-gnu-${MULTIRUN_VERSION}.tar.gz /tmp
RUN tar -xf /tmp/multirun-x86_64-linux-gnu-${MULTIRUN_VERSION}.tar.gz \
    && mv multirun /bin \
    && rm /tmp/*

RUN chown appuser:appuser /app
USER appuser

RUN pip install --upgrade pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --dev --deploy

COPY . /app/
COPY --from=cssbuild /app/trojstenid/users/static/app.css /app/trojstenid/users/static/app.css

CMD ["/bin/multirun", "caddy run --config /app/Caddyfile", "/app/start.sh"]
