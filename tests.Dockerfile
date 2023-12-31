# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/


ARG PYTHON_VERSION=3.11.4
FROM python:${PYTHON_VERSION}-slim-bullseye as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.

RUN apt-get update && \
    apt-get install -y libpq-dev gcc

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements-tests.txt,target=requirements-tests.txt \
    python -m pip install -r requirements-tests.txt

# Copy the source code into the container.
COPY --chown=appuser:appuser *.py ./
COPY --chown=appuser:appuser ./src ./src
COPY --chown=appuser:appuser ./Tests ./Tests

# Add permissions for app folder (pytest creating .pytest_cache folders)
RUN chown appuser:appuser ./

# Switch to the non-privileged user to run the application.
USER appuser

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
ENTRYPOINT ["python", "-m", "pytest", "-v", "--ff", "--tb=no", "-l", "--asyncio-mode=auto"]
