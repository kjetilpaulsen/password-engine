# password-engine

### Description

A Python application for secure password generation, storage, and retrieval, with encryption at rest and user-based access control.

> **Note**
>
> This project is currently in migration from the python-project-blueprint template.  
> The command structure is temporarily not fully implemented.  
> User input is currently handled directly in handlers instead of through the command system.  
> This will be refactored shortly to restore proper command → handler → event flow.

### What this is

This repository is a **work-in-progress application** built on top of a modular Python architecture.

It aims to provide:
- Secure password generation
- Encrypted password storage
- User-based authentication and access
- CLI-first workflow (API support planned)

## Table of contents:
 - Quick start
 - Features
 - Architecture
 - Installation
   - Requirements
   - Setup
   - Usage
   - Testing
 - Docker & Github Actions
   - Local docker usage
   - GitHub Actions setup

## Quick Start

```bash
git clone https://github.com/kjetilpaulsen/password-engine.git
cd password-engine
uv sync
```

Run CLI (current state is partially hardcoded flow):

```bash
uv run python -m password_engine cli version
```

## Features

- Password generation (randomized secure strings)
- Encrypted storage of passwords (at rest)
- User-based access (username + password unlock flow)
- CLI entrypoint (currently the only one working)
- FastAPI entrypoint 
- Command → Handler → Event architecture (partially implemented)
- Shared core between CLI and API
- Structured runtime configuration (env → config → defaults)
- XDG-compliant directory layout
- Logging system (file + console + stderr)
- Pydantic-based settings
- Test support (pytest + coverage)
- Docker support
- CI/CD with GitHub Actions (partially configured)

## Architecture

### Architecture
[Architecture](docs/architecture.md)

### Flow
[Flow](docs/flow.md)

## Installation

### Requirements
- **Python** ≥ 3.11 (recommended: 3.12–3.14)
- **uv**

### Setup
```bash
git clone https://github.com/kjetilpaulsen/password-engine.git
cd password-engine
uv sync
```

Optional:
```bash
source .venv/bin/activate
```

## Usage

> Current state: command system is not fully wired

The intended functionality:

### List passwords
```bash
uv run python -m password-engine --list-passwords
```

### Generate password
```bash
uv run python -m password-engine --generate-password
```

### Current temporary flow

- Prompts for:
  - username (optional → defaults to system user)
  - password
- Credentials are hashed
- Used to unlock encrypted storage
- Depending on mode:
  - List stored passwords
  - Generate new password → confirm → store

### API mode (experimental)

```bash
uv run python -m password_engine api
```

Health check:
```bash
curl http://127.0.0.1:8001/health
```

## Testing

```bash
uv run pytest
```

With coverage:
```bash
uv run pytest -V --cov=password_engine --cov-report=term-missing
```

## Docker & GitHub Actions Setup

### Overview

- Docker: builds and runs the API
- Docker Compose: local container orchestration
- GitHub Actions: test + build + push image (currently unstable)

## Local Docker Usage

### 1. Create `.env`

```env
IMAGE_NAME=<your-dockerhub-username>/<your-image-name>
IMAGE_TAG=latest

LOG_LEVEL=DEBUG
CONSOLE_LOG=true
STDERR_LOG=true
```

### 2. Build and run

```bash
docker compose up --build
```

Stop:
```bash
docker compose down
```

Test:
```bash
curl http://127.0.0.1:8010/health
```

## GitHub Actions usage

> Note: CI/CD and Postgres integration are currently not fully stable

### Setup secrets

```bash
DOCKERHUB_USERNAME=<username>
```
```bash
DOCKERHUB_TOKEN=<token>
```
```bash
IMAGE_NAME=<username>/<repo>
```
```bash
IMAGE_TAG_LATEST=<repo>
```
```bash
PREFIX_SHA=<repo>
```

On push to `release` branch:
- runs tests
- builds Docker image
- pushes to DockerHub

