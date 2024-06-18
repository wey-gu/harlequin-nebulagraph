![Harlequin NebulaGraph Adapter](https://raw.githubusercontent.com/wey-gu/harlequin-nebulagraph/main/assets/harlequin-nebulagraph-banner.png)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/harlequin)
![Runs on Linux | MacOS | Windows](https://img.shields.io/badge/runs%20on-Linux%20%7C%20MacOS%20%7C%20Windows-blue)

[![CI](https://github.com/wey-gu/harlequin-nebulagraph/actions/workflows/pypi.yaml/badge.svg)](https://github.com/wey-gu/harlequin-nebulagraph/actions/workflows/pypi.yaml)
[![for NebulaGraph](https://img.shields.io/badge/Toolchain-NebulaGraph-blue)](https://github.com/vesoft-inc/nebula) [![GitHub release (latest by date)](https://img.shields.io/github/v/release/wey-gu/harlequin-nebulagraph?label=Version)](https://github.com/wey-gu/harlequin-nebulagraph/releases)
[![pypi-version](https://img.shields.io/pypi/v/harlequin-nebulagraph)](https://pypi.org/project/harlequin-nebulagraph/)
[![Documentation](https://img.shields.io/badge/docs-Read%20The%20Docs-blue)](https://harlequin.sh/docs/nebulagraph/index)

`harlequin-nebulagraph` is a NebulaGraph adapter for [Harlequin](https://github.com/tconbeer/harlequin), a Database IDE for the terminal.

https://github.com/wey-gu/harlequin-nebulagraph/assets/1651790/b27c0ea2-4080-4313-9607-285e477d1898

## Getting Started

1. Install the adapter: `pip install harlequin-nebulagraph`

2. Run `harlequin -a nebulagraph` to start the terminal

Defaults to `localhost:9669`, `root`, and `password`. You can override these with the following environment variables:

```bash
harlequin -a nebulagraph -h 127.0.0.1 -p 9669 -u root --password password
```

## Documentation

For more information about the adapter, see the [Harlequin Docs](https://harlequin.sh/docs/nebulagraph/index).
