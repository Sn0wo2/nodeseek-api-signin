import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom

n, p = 50, 0.1
samples = 1000
data = np.random.binomial(n, p, samples)

fig, ax = plt.subplots(figsize=(8, 4.5))

ax.hist(data, bins=np.arange(-0.5, n+1.5, 1),
        density=True, alpha=0.6, color='steelblue',
        edgecolor='white', label=f'Sample (n={n}, p={p}, N={samples})')

x = np.arange(0, n+1)
ax.plot(x, binom.pmf(x, n, p), 'o-', color='crimson',
        markersize=4, label='Theoretical PMF')

ax.axvline(np.mean(data), color='orange', linestyle='--',
           label=f'Sample mean = {np.mean(data):.2f}')
ax.axvline(n*p, color='gray', linestyle=':',
           label=f'Theoretical mean = {n*p}')

ax.set_xlabel('k (successes)')
ax.set_ylabel('Probability / Frequency density')
ax.set_title(f'Binomial Distribution B({n}, {p}) — {samples} samples')
ax.set_xlim(-1, 18)
ax.legend(loc='upper right', fontsize=8)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()