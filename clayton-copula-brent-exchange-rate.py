import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# 1. Generación de datos sintéticos representativos del mercado colombiano
# -----------------------------------------------------------------------------
np.random.seed(42)
n_obs = 1000

# Retornos diarios simulados con dependencia asimétrica en colas
mean = [0, 0]
cov = [[1, -0.50], [-0.50, 1]]
x1, x2 = np.random.multivariate_normal(mean, cov, n_obs).T

# Inyección de shock petrolero: caídas extremas en Brent impulsan el USD/COP
shock_mask = x1 < -1.2
x2[shock_mask] += np.abs(x1[shock_mask]) * 0.75

df = pd.DataFrame({
    'Brent_Returns': x1,
    'USDCOP_Returns': x2
})

# -----------------------------------------------------------------------------
# 2. Transformación a Uniformes U(0,1) mediante Distribución Empírica (EDF)
# -----------------------------------------------------------------------------
# Pseudo-observaciones en el hipercubo unitario [0, 1]^2
u1 = stats.rankdata(df['Brent_Returns']) / (len(df) + 1)
u2 = stats.rankdata(df['USDCOP_Returns']) / (len(df) + 1)

# Invertimos u2 para analizar la cola inferior conjunta (caída Brent y subida USD/COP)
u2_inv = 1 - u2

# -----------------------------------------------------------------------------
# 3. Definición de la Log-Verosimilitud de la Cópula Clayton
# -----------------------------------------------------------------------------
def clayton_log_likelihood(theta, u, v):
    """
    Densidad c(u,v) = (1+theta) * (u*v)^(-1-theta) * (u^-theta + v^-theta - 1)^(-2 - 1/theta)
    """
    if theta <= 0:
        return 1e10
    
    term1 = np.log(1 + theta)
    term2 = (-1 - theta) * (np.log(u) + np.log(v))
    base = u**(-theta) + v**(-theta) - 1
    
    # Penalizar valores fuera del dominio
    if np.any(base <= 0):
        return 1e10
        
    term3 = (-2 - (1 / theta)) * np.log(base)
    log_pdf = term1 + term2 + term3
    
    return -np.sum(log_pdf)  # Se retorna en negativo para minimizar

# -----------------------------------------------------------------------------
# 4. Estimación del Parámetro Theta (θ) mediante Máxima Verosimilitud
# -----------------------------------------------------------------------------
opt_result = minimize(
    clayton_log_likelihood, 
    x0=[1.0], 
    args=(u1, u2_inv), 
    bounds=[(1e-4, 20.0)],
    method='L-BFGS-B'
)

theta_hat = opt_result.x[0]

# Coeficiente de Dependencia en la Cola Inferior (\lambda_L)
lambda_L = 2 ** (-1 / theta_hat)
tau_kendall = theta_hat / (theta_hat + 2)

print("="*60)
print(" RESULTADOS DE LA ESTIMACIÓN DE CÓPULA (CASO COLOMBIA)")
print("="*60)
print(f"Parámetro theta (θ) estimado : {theta_hat:.4f}")
print(f"Tau de Kendall (τ) implícito  : {tau_kendall:.4f}")
print(f"Dependencia en Cola (λ_L)     : {lambda_L:.4f}")
print("="*60)

# -----------------------------------------------------------------------------
# 5. Visualización de Pseudo-observaciones en el Espacio de la Cópula
# -----------------------------------------------------------------------------
plt.figure(figsize=(8, 6))
plt.scatter(u1, u2_inv, alpha=0.5, color='darkblue', edgecolors='none', s=20)
plt.title(f'Espacio de la Cópula: Brent vs USD/COP (θ = {theta_hat:.2f})', fontsize=12)
plt.xlabel('U1 (Brent Returns Rank)')
plt.ylabel('1 - U2 (USD/COP Returns Rank Invertido)')
plt.grid(True, linestyle='--', alpha=0.5)
plt.axvline(0.1, color='red', linestyle=':', label='Zona de Cola extrema (< 10%)')
plt.axhline(0.1, color='red', linestyle=':')
plt.legend()
plt.tight_layout()
plt.show()