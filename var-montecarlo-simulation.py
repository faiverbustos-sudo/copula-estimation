import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt

np.random.seed(42)
n_simulations = 10000
portfolio_value_cop = 1_000_000_000  # $1,000 millones COP
w1, w2 = 0.50, 0.50                   # Pesos del portafolio

# Parámetros estimados en la fase anterior
theta_clayton = 1.0831

# Parámetros GARCH(1,1) estimados
# [omega, alpha, beta, varianza_ultimo_periodo, ultimo_retorno]
garch_brent = {'omega': 0.0656, 'alpha': 0.1203, 'beta': 0.8068, 'sigma2_t': 1.20, 'r_t': -1.5}
garch_usdcop = {'omega': 0.2254, 'alpha': 0.1725, 'beta': 0.7664, 'sigma2_t': 1.80, 'r_t': 1.8}

# -----------------------------------------------------------------------------
# 1. Proyección de Volatilidad a t+1 con las ecuaciones GARCH
# -----------------------------------------------------------------------------
sigma2_brent_t1 = garch_brent['omega'] + garch_brent['alpha'] * (garch_brent['r_t']**2) + garch_brent['beta'] * garch_brent['sigma2_t']
sigma2_usdcop_t1 = garch_usdcop['omega'] + garch_usdcop['alpha'] * (garch_usdcop['r_t']**2) + garch_usdcop['beta'] * garch_usdcop['sigma2_t']

sigma_brent_t1 = np.sqrt(sigma2_brent_t1)
sigma_usdcop_t1 = np.sqrt(sigma2_usdcop_t1)

# -----------------------------------------------------------------------------
# 2. Muestreo Aleatorio de la Cópula Clayton
# -----------------------------------------------------------------------------
# Algoritmo de generación condicional para Cópula Clayton
v1 = np.random.uniform(0, 1, n_simulations)
v2 = np.random.uniform(0, 1, n_simulations)

u1_sim = v1
u2_sim = (v1**(-theta_clayton) * (v2**(-theta_clayton / (1 + theta_clayton)) - 1) + 1)**(-1 / theta_clayton)

# Invertimos u2 para reflejar la relación inversa (caída Brent -> subida USD/COP)
u2_sim_inv = 1 - u2_sim

# -----------------------------------------------------------------------------
# 3. Transformación a Residuos Estandarizados (Z) y Retornos Proyectados
# -----------------------------------------------------------------------------
z1_sim = stats.norm.ppf(np.clip(u1_sim, 1e-6, 1 - 1e-6))
z2_sim = stats.norm.ppf(np.clip(u2_sim_inv, 1e-6, 1 - 1e-6))

# Retornos simulados con escala de volatilidad proyectada (en %)
r1_sim = z1_sim * sigma_brent_t1
r2_sim = z2_sim * sigma_usdcop_t1

# Rendimiento simulado del Portafolio
r_portafolio = (w1 * r1_sim) + (w2 * r2_sim)
pérdidas_cop = -(r_portafolio / 100) * portfolio_value_cop

# -----------------------------------------------------------------------------
# 4. Cálculo del Value at Risk (VaR) y Expected Shortfall (CVaR)
# -----------------------------------------------------------------------------
alpha_95 = 95
alpha_99 = 99

var_95_pct = np.percentile(r_portafolio, 100 - alpha_95)
var_99_pct = np.percentile(r_portafolio, 100 - alpha_99)

var_95_cop = np.percentile(pérdidas_cop, alpha_95)
var_99_cop = np.percentile(pérdidas_cop, alpha_99)

# Expected Shortfall (CVaR): promedio de las pérdidas que superan el VaR
cvar_95_cop = pérdidas_cop[pérdidas_cop >= var_95_cop].mean()
cvar_99_cop = pérdidas_cop[pérdidas_cop >= var_99_cop].mean()

print("="*65)
print(f" MÉTRICAS DE RIESGO DE PORTAFOLIO (VALOR: ${portfolio_value_cop:,.0f} COP)")
print("="*65)
print(f"Volatilidad Proyectada (1 día) - Brent   : {sigma_brent_t1:.2f}%")
print(f"Volatilidad Proyectada (1 día) - USD/COP : {sigma_usdcop_t1:.2f}%")
print("-" * 65)
print(f"VaR 95% (1 día)  : {var_95_pct:.2f}%  --> Pérdida Máxima: ${var_95_cop:,.0f} COP")
print(f"VaR 99% (1 día)  : {var_99_pct:.2f}%  --> Pérdida Máxima: ${var_99_cop:,.0f} COP")
print("-" * 65)
print(f"CVaR 95% (Expected Shortfall) : ${cvar_95_cop:,.0f} COP")
print(f"CVaR 99% (Expected Shortfall) : ${cvar_99_cop:,.0f} COP")
print("="*65)

# -----------------------------------------------------------------------------
# 5. Histogramas de Rendimientos y Zona de Pérdida Extrema
# -----------------------------------------------------------------------------
plt.figure(figsize=(10, 6))
plt.hist(pérdidas_cop / 1e6, bins=60, color='slategray', edgecolor='black', alpha=0.7)
plt.axvline(var_95_cop / 1e6, color='orange', linestyle='--', linewidth=2, label=f'VaR 95%: ${var_95_cop/1e6:,.1f}M COP')
plt.axvline(var_99_cop / 1e6, color='red', linestyle='--', linewidth=2, label=f'VaR 99%: ${var_99_cop/1e6:,.1f}M COP')
plt.axvline(cvar_99_cop / 1e6, color='darkred', linestyle=':', linewidth=2, label=f'CVaR 99%: ${cvar_99_cop/1e6:,.1f}M COP')

plt.title('Distribución de Pérdidas Simuladas a 1 Día (Cópula Clayton - GARCH)', fontsize=12)
plt.xlabel('Pérdida en Millones de Pesos COP')
plt.ylabel('Frecuencia de Escenarios (Simulaciones Monte Carlo)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()