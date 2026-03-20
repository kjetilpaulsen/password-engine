# password-engine

This is an old project, but early in March 2026 I started migrating the old code into this repo. I am combining it with my python-project-blueprint repo in order to harden the surrounding infrastructure in the app. As a result not all features have been migrated yet, and the README.md is lacking. My first priority is to get the README.md up and running, which should be by 23 March 2026

A backend tool for generating, storing and later listing passwords.

## Features
- Two entrypoints, CLI/FastAPI
- Structured logging
- XDG folder structure
- Uses argon2 and cryptography
- Hashing of user login passwords
- Encryption at rest for stored passwords
- Supports multiple users, and setting user passwords, including confirmation of password

## Installation

### Requirements
- Python >= 3.x

### Setup
```bash
git clone https://github.com/kjetilpaulsen/password-engine.git
cd password-engine
```

