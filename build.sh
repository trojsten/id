#!/bin/bash
# This script finishes all build-time requirements.
set -euo pipefail

export DATABASE_URL=sqlite://:memory:
export TROJSTEN_LOGIN_CLIENT=not-provided
export TROJSTEN_LOGIN_SECRET=not-provided
export RECAPTCHA_PUBLIC=not-provided
export RECAPTCHA_PRIVATE=not-provided
export OIDC_KEY=not-provided

python manage.py collectstatic --no-input
