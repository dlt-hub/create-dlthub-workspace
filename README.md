# create-dlthub-workspace

Scaffold a dltHub workspace from the official starter project.

```bash
uvx create-dlthub-workspace my-project
```

The CLI downloads the starter scaffold, ensures `uv` is available, runs `uv sync`,
initializes the selected AI workbench, installs all supported dltHub AI toolkits,
and prints next steps.

```bash
create-dlthub-workspace my-project --agent claude
create-dlthub-workspace my-project --agent cursor --yes
create-dlthub-workspace my-project --skip-uv-sync
```

For local setup, testing, and build commands, see [CONTRIBUTING.md](CONTRIBUTING.md).
