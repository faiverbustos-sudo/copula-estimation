import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.optimize import minimize
from arch import arch_model
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# 1. Simulación de Series con Volatilidad Condicional (GARCH) y Shocks Conjuntos
# -----------------------------------------------------------------------------
np.random.seed(42)
n_obs = 1200

# Innovaciones estandarizadas con dependencia asimétrica
cov = [[1.0, -0.45], [-0.45, 1.0]]
z1, z2 = np.random.multivariate_normal([0, 0], cov, n_obs).T

# Inyección de dependencia no lineal en la cola extrema inferior
shock_idx = z1 < -1.3
z2[shock_idx] += np.abs(z1[shock_idx]) * 0.80

# Generar volúmenes de volatilidad GARCH(1,1) para Brent y USD/COP
sigma1 = np.zeros(n_obs)
sigma2 = np.zeros(n_obs)
r1 = np.zeros(n_obs)
r2 = np.zeros(n_obs)

omega1, alpha1, beta1 = 0.05, 0.10, 0.85
omega2, alpha2, beta2 = 0.08, 0.12, 0.82

sigma1[0], sigma2[0] = 1.0, 1.0

for t in range(1, n_obs):
    sigma1[t] = np.sqrt(omega1 + alpha1 * (r1[t-1]**2) + beta1 * (sigma1[t-1]**2))
    sigma2[t] = np.sqrt(omega2 + alpha2 * (r2[t-1]**2) + beta2 * (sigma2[t-1]**2))
    r1[t] = z1[t] * sigma1[t]      # Retornos Brent
    r2[t] = z2[t] * sigma2[t]      # Retornos USD/COP

df_returns = pd.DataFrame({'Brent': r1, 'USDCOP': r2})

# -----------------------------------------------------------------------------
# 2. Filtrado ARMA-GARCH de las Distribuciones Marginales
# -----------------------------------------------------------------------------
def fit_garch(series, name):
    # Modelo GARCH(1,1) con media constante
    model = arch_model(series, mean='Constant', vol='GARCH', p=1, q=1, dist='normal')
    res = model.fit(disp='off')
    # Residuos estandarizados z_t = e_t / sigma_t
    std_resid = res.resid / res.conditional_volatility
    return std_resid, res.conditional_volatility, res

z_brent, vol_brent, model_brent = fit_garch(df_returns['Brent'], 'Brent')
z_usdcop, vol_usdcop, model_usdcop = fit_garch(df_returns['USDCOP'], 'USD/COP')

print("="*65)
print(" RESUMEN DEL FILTRADO GARCH(1,1)")
print("="*65)
print(f"Brent  - Omega: {model_brent.params['omega']:.4f}, Alpha: {model_brent.params['alpha[1]']:.4f}, Beta: {model_brent.params['beta[1]']:.4f}")
print(f"USDCOP - Omega: {model_usdcop.params['omega']:.4f}, Alpha: {model_usdcop.params['alpha[1]']:.4f}, Beta: {model_usdcop.params['beta[1]']:.4f}")

# -----------------------------------------------------------------------------
# 3. Transformación Integral de la Probabilidad (PIT) a Uniformes U(0,1)
# -----------------------------------------------------------------------------
# Convertimos los residuos estandarizados a pseudo-observaciones uniformes
u1 = stats.rankdata(z_brent) / (len(z_brent) + 1)
u2 = stats.rankdata(z_usdcop) / (len(z_usdcop) + 1)

# Invertimos u2 para evaluar la caida del Brent y el incremento del USD/COP
u2_inv = 1 - u2

# -----------------------------------------------------------------------------
# 4. Estimación de la Cópula Clayton sobre los Residuos I.I.D.
# -----------------------------------------------------------------------------
def clayton_log_likelihood(theta, u, v):
    if theta <= 0:
        return 1e10
    term1 = np.log(1 + theta)
    term2 = (-1 - theta) * (np.log(u) + np.log(v))
    base = u**(-theta) + v**(-theta) - 1
    if np.any(base <= 0):
        return 1e10
    term3 = (-2 - (1 / theta)) * np.log(base)
    return -np.sum(term1 + term2 + term3)

res_copula = minimize(
    clayton_log_likelihood, 
    x0=[1.0], 
    args=(u1, u2_inv), 
    bounds=[(1e-4, 20.0)],
    method='L-BFGS-B'
)

theta_hat = res_copula.x[0]
lambda_L = 2 ** (-1 / theta_hat)
tau_kendall = theta_hat / (theta_hat + 2)

print("\n" + "="*65)
print(" RESULTADOS CÓPULA CLAYTON SOBRE RESIDUOS GARCH")
print("="*65)
print(f"Parámetro Theta (θ)  : {theta_hat:.4f}")
print(f"Tau de Kendall (τ)   : {tau_kendall:.4f}")
print(f"Dependencia Cola (λ_L): {lambda_L:.4f}")
print("="*65)

# -----------------------------------------------------------------------------
# 5. Visualización: Volatilidad Filtrada vs. Residuos en el Espacio Cópula
# -----------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Grafico 1: Volatilidad Condicional Filtrada
axes[0].plot(vol_brent, label='Volatilidad Condicional Brent', color='navy', alpha=0.8)
axes[0].plot(vol_usdcop, label='Volatilidad Condicional USD/COP', color='crimson', alpha=0.8)
axes[0].set_title('Volatilidad Condicional Filtrada (GARCH 1,1)')
axes[0].set_ylabel('Sigma (σ_t)')
axes[0].legend()
axes[0].grid(True, linestyle='--', alpha=0.5)

# Grafico 2: Espacio de Cópula con Residuos
axes[1].scatter(u1, u2_inv, alpha=0.4, color='teal', s=18)
axes[1].set_title(f'Cópula sobre Residuos GARCH (θ = {theta_hat:.2f})')
axes[1].set_xlabel('U1 (Residuos Estandarizados Brent)')
axes[1].set_ylabel('1 - U2 (Residuos Estandarizados USD/COP Invertido)')
axes[1].grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()