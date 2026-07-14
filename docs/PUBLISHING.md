# Publishing Recall to PyPI

The repo is wired for **PyPI Trusted Publishing** — GitHub Actions publishes automatically when you create a release. No API token to create, store, or leak.

> **Note:** `recall-terminal` already exists on PyPI (versions 0.1.0–0.1.2, uploaded 4 June 2026 with this project's tagline). If that's your account, the setup below just works. If it's *not* yours, pick a new name (e.g. `recall-cli`, `recall-dev`) in `pyproject.toml` → `[project] name` and in `.github/workflows/publish.yml` → `environment.url`, then follow the same steps.

## One-time setup (~5 minutes)

1. **PyPI account** — log in at https://pypi.org (the account that owns `recall-terminal`).
2. **Add a trusted publisher** — go to the project page → *Manage* → *Publishing* → *Add a new publisher*, and enter exactly:
   - Owner: `mbilalrehman`
   - Repository: `Recall-terminal`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`
3. **Create the GitHub environment** — repo → *Settings* → *Environments* → *New environment* → name it `pypi`. (Optional but recommended: add yourself as a required reviewer so nothing publishes without your click.)

## Releasing a new version

1. Bump the version in **both** places (they must match):
   - `pyproject.toml` → `version = "0.2.0"`
   - `recall/__init__.py` → `__version__ = "0.2.0"`
2. Commit, push, and make sure CI is green.
3. Create the release:
   - GitHub → *Releases* → *Draft a new release* → tag `v0.2.0` → *Publish release*.
4. The `Publish to PyPI` workflow builds, smoke-tests the wheel, and uploads. A few minutes later:

```bash
pip install recall-terminal
```

PyPI never allows re-uploading a version number — every release needs a bump, even for a one-line fix.

## Publishing manually from your machine (fallback)

```bash
python -m pip install build twine
python -m build
python -m twine upload dist/*   # will ask for a PyPI API token
```
