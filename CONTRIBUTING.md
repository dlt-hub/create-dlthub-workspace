# Contributing

This project uses a standard `src/` layout and `uv` for local development.

## Setup

Install dependencies into a local virtual environment:

```bash
make dev
```

Run the CLI from the checkout:

```bash
uv run create-dlthub-workspace --help
```

Create a workspace with defaults:

```bash
uv run create-dlthub-workspace my-workspace --yes
```

Choose an AI workbench explicitly:

```bash
uv run create-dlthub-workspace my-workspace --agent claude
uv run create-dlthub-workspace my-workspace --agent cursor
uv run create-dlthub-workspace my-workspace --agent codex
```

## Tests

Run the unit test suite:

```bash
make test
```

Run a quick syntax check:

```bash
make compile
```

## Build

Build the source distribution and wheel:

```bash
make build
```

The build artifacts are written to `dist/`.

## Release Notes

Before publishing, verify:

```bash
uv run create-dlthub-workspace --help
make ci
```

The package exposes two console commands:

```text
create-dlthub-workspace
create-dlthub-project
```
