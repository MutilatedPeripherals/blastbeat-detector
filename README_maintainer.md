# Maintainer guide

Instructions for publishing new releases of `blastbeat_detector` to TestPyPI/PyPI.

## Release checklist

1. Bump the version in `pyproject.toml` (patch for bugfixes, minor for features):

   ```toml
   [project]
   version = "0.0.7"
   ```

2. Build the distributions (from the repo root):

   ```bash
   python -m build
   ```

3. Verify the metadata:

   ```bash
   python -m twine check dist/*
   ```

4. Upload to the desired index:

   ```bash
   # TestPyPI (use this first!)
   python -m twine upload --repository testpypi dist/*

   # PyPI (only after the TestPyPI release looks good)
   python -m twine upload dist/*
   ```

## Troubleshooting

- **`InvalidDistribution: Invalid distribution metadata: '2.5' is not a valid metadata version`**
  The latest `hatchling` emits `Metadata-Version: 2.5`, which older twine versions reject.
  Upgrading twine fixes it:

  ```bash
  python -m pip install --upgrade twine
  ```

- **"File already exists" on upload**
  TestPyPI and PyPI reject re-uploads of the same version. Bump the version instead.

- **Stale `dist/` artifacts**
  Old wheels/sdists can trip up `twine check`; clear them before rebuilding:

  ```bash
  rm -rf dist && python -m build
  ```

## Environment setup

```bash
python -m pip install build twine
```