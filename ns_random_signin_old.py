import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import expon

lambda_param = 0.2
samples = 1000
data = np.random.exponential(scale=1/lambda_param, size=samples)

fig, ax = plt.subplots(figsize=(8, 4.5))

ax.hist(data, bins=np.arange(0, 51, 1),
        density=True, alpha=0.6, color='steelblue',
        edgecolor='white', label=f'Sample (λ={lambda_param}, N={samples})')

x = np.linspace(0, 50, 500)
ax.plot(x, expon.pdf(x, scale=1/lambda_param), color='crimson',
        linewidth=2, label='Theoretical PDF')

ax.axvline(np.mean(data), color='orange', linestyle='--',
           label=f'Sample mean = {np.mean(data):.2f}')
ax.axvline(1/lambda_param, color='gray', linestyle=':',
           label=f'Theoretical mean = {1/lambda_param}')

x_tail = np.linspace(40, 50, 100)
y_tail = expon.pdf(x_tail, scale=1/lambda_param)
ax.fill_between(x_tail, y_tail, alpha=0.3, color='orange',
                label=f'P(X ≥ 40) ≈ {np.exp(-lambda_param*40)*1000:.3f}‰')

ax.set_xlabel('x (chicken legs)')
ax.set_ylabel('Probability Density f(x)')
ax.set_title(f'Exponential Distribution Exp(λ={lambda_param}) — {samples} samples')
ax.set_xlim(0, 50)
ax.legend(loc='upper right', fontsize=8)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()