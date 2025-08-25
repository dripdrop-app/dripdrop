## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- make
- [docker](https://docs.docker.com/engine/install/)
- [infisical](https://infisical.com/docs/cli/overview)
- [nvm](https://github.com/nvm-sh/nvm)

## Setup

After installing all requirements run this command to initialize the repo:

```bash
make install
```

## Run

To run the development server run this command

```bash
make server-dev
```

To run the development worker run this command

```bash
make worker-dev
```

To run the development client run this command

```bash
make client-dev
```

To run all three development services run this command

```bash
make dev
```

## Test

Run this command to execute tests.

**NOTE**: Ensure services are running before executing this command.

```bash
make test
```
