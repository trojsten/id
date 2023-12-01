FROM node:21.2.0-alpine AS cssbuild

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY trojstenid ./trojstenid
COPY tailwind.config.js ./
RUN npm run css-prod
CMD ["npm", "run", "css-dev"]

FROM python:3.11-slim-bookworm
WORKDIR /app
RUN useradd --create-home appuser

ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1
ENV PATH=/home/appuser/.local/bin:$PATH

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt update \
    && apt -y upgrade \
    && apt -y clean \
    && rm -rf /var/lib/apt/lists/*

USER appuser

RUN pip install --upgrade pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --dev --deploy

COPY . /app/
COPY --from=cssbuild /app/trojstenid/users/static/app.css /app/trojstenid/users/static/app.css

CMD ["/app/start.sh"]
