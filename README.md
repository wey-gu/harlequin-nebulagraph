![Harlequin NebulaGraph Adapter](https://raw.githubusercontent.com/wey-gu/harlequin-nebulagraph/main/assets/harlequin-nebulagraph-banner.png)

`harlequin-nebulagraph` is a NebulaGraph adapter for [Harlequin](https://github.com/tconbeer/harlequin), a Database IDE for the terminal.

This adapter will use Application Default Credentials to authenticate with NebulaGraph and run queries.

## Getting Started

1. Install the adapter: `pip install harlequin-nebulagraph`

2. Run `harlequin -a nebulagraph` to start the terminal

Defaults to `localhost:9669`, `root`, and `password`. You can override these with the following environment variables:

```bash
harlequin -a nebulagraph -h 127.0.0.1 -p 9669 -u root -P password
```

## Documentation

For more information about the adapter, see the [Harlequin Docs](https://harlequin.sh/docs/nebulagraph/index).