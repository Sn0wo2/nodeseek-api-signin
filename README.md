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
- `COOKIE_STORE`: required cookie write-back backend. Set it explicitly to `github`,
  `qinglong`, or `none`; `auto` is not supported.
- `COOKIE_WRITEBACK`: optional write-back switch. Defaults to enabled for
  `github`/`qinglong` stores and disabled for `none`.
- `PROXY_URL`: optional HTTP/HTTPS proxy URL.
- `TIMEOUT`: optional request timeout in seconds.
- `LOG_LEVEL`: optional logging level. Set to `DEBUG` to print HTTP response HTML.

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

## About `Signin Mode`

Before you consider adjusting the `Signin Mode`, here's what you need to know.

### Mechanism Overview

The chicken leg reward generation has shifted from an **exponential distribution** to a **binomial distribution**:

| Mechanism | Distribution | Expectation | Variance | Std Dev |
|-----------|-------------|-------------|----------|---------|
| Old | Exponential $\text{Exp}(\lambda=0.2)$ | $5$ | $25$ | $5$ |
| New | Binomial $B(50, 0.1)$ | $5$ | $4.5$ | $\approx 2.12$ |

**Key takeaway**: Both mechanisms share the same mathematical expectation ($5$), but the new one drastically reduces variance to improve user experience.

---

### Old Mechanism: Exponential Distribution

Probability density function:

$$
f(x) = \lambda e^{-\lambda x} = 0.2 \, e^{-0.2x}, \quad x \geq 0
$$

where the rate parameter $\lambda = \frac{1}{E[X]} = 0.2$.

**Pain points**:
- Rolling $1$ chicken leg was far too likely (~$14.84\%$ after flooring), killing motivation
- Massive variance ($\text{Var}(X) = 25$) created extreme disparity between lucky and unlucky users
- Rare "jackpot" events: $P(X \geq 40) = e^{-8} \approx 0.335‰$

---

### New Mechanism: Binomial Distribution

Probability mass function:

$$
P(X = k) = \binom{50}{k} (0.1)^k (0.9)^{50-k}, \quad k = 0, 1, 2, \ldots, 50
$$

The system enforces a floor of $1$, so actual payout is:

$$
\text{reward} = \max(X, 1)
$$

**Improvements**:
- Probability of getting exactly $1$ drops to ~$0.52\%$ (pre-truncation $P(X=0) \approx 0.51\%$)
- Variance compressed to $4.5$; most users land in the $3 \sim 7$ range
- Extreme jackpots ($40+$) are eliminated (theoretical cap is $50$)

---

### Code Locations

- **New mechanism (binomial visualization)**: `ns_raindom_signin.py`
- **Old mechanism (exponential visualization)**: `ns_random_signin_old.py`

> Note: The old mechanism had the same expectation of $5$, but its exponential tail made rolling $1$ far too common. Hence the distribution was changed.
> Source: [NodeSeek post #1170](https://www.nodeseek.com/post-1170-1)