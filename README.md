# NodeSeek API Signin

Python script for signing in to NodeSeek with cookie-based account configuration.

## Usage

Install dependencies:

```powershell
poetry install
```

Run the signin script:

```powershell
poetry run python -m nodeseek_signin
```

## Environment

- `NS_COOKIE`: required. Use `&` to separate multiple account cookies.
- `BASE_URL`: optional NodeSeek base URL. Defaults to `https://www.nodeseek.com`.
- `NS_RANDOM`: optional. Set to `true` to use random signin mode.
- `ENABLE_STATISTICS`: optional. Set to `false` to skip statistics lookup.
- `COOKIE_STORE`: optional cookie write-back backend. Use `auto`, `github`,
  `qinglong`, or `none`. Defaults to `auto`.
- `COOKIE_WRITEBACK`: optional write-back switch. Defaults to enabled for
  explicit `github`/`qinglong` stores and in GitHub Actions, disabled locally.
- `PROXY_URL`: optional HTTP/HTTPS proxy URL.
- `TIMEOUT`: optional request timeout in seconds.

## GitHub Actions Secrets

- `NS_COOKIE`: NodeSeek cookie string.
- `NS_COOKIE_WRITE_TOKEN`: PAT used only to update `NS_COOKIE` when NodeSeek refreshes cookies.

The PAT must be able to write Actions secrets for this repository. Use a fine-grained PAT
scoped to this repository with repository secrets write access, or a classic PAT with the
minimum repository access your account allows.

## QingLong

Run as a QingLong task and set:

```text
COOKIE_STORE=qinglong
```

When NodeSeek refreshes cookies, `NS_COOKIE` is written back through QingLong's
built-in `QLAPI` (injected into the task runtime), so no URL, token, or API
credentials are needed. The `NS_COOKIE` environment variable must already exist
in QingLong, and the script must run inside the panel (`QLAPI` is unavailable
otherwise). Multiple accounts still use `&` as the separator.
