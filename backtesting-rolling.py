import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# 1. Simulación de Serie Histórica de Pérdidas y VaR Estimado
# -----------------------------------------------------------------------------
np.random.seed(101)
N = 750  # Días de backtesting fuera de muestra

# Generación de pérdidas reales del portafolio (en % de retorno)
# Asumimos que ocurren shocks de cola ocasionales
returns_real = np.random.standard_t(df=5, size=N) * 1.2

# Generación del VaR al 95% y 99% estimado por Cópula-GARCH
var_95_series = np.full(N, -np.percentile(returns_real, 5))
var_99_series = np.full(N, -np.percentile(returns_real, 1))

# Ajuste dinámico de volatilidad en el VaR estimado
vol_factor = np.abs(np.sin(np.linspace(0, 10, N))) * 0.5 + 0.8
var_95_series = var_95_series * vol_factor
var_99_series = var_99_series * vol_factor

# -----------------------------------------------------------------------------
# 2. Identificación de Violaciones (Excepciones)
# -----------------------------------------------------------------------------
# Ocurre una violación cuando la pérdida real es peor que el VaR (-retorno > VaR)
pérdidas_reales = -returns_real

violaciones_95 = pérdidas_reales > var_95_series
violaciones_99 = pérdidas_reales > var_99_series

x_95 = np.sum(violaciones_95)
x_99 = np.sum(violaciones_99)

# -----------------------------------------------------------------------------
# 3. Función para la Prueba de Razón de Verosimilitud de Kupiec (POF)
# -----------------------------------------------------------------------------
def kupiec_test(x, N, alpha_level):
    p_teorico = 1 - alpha_level
    p_observado = x / N
    
    if x == 0:
        return 0.0, 1.0, p_observado
        
    # Razón de verosimilitud (Likelihood Ratio)
    num = (p_teorico**x) * ((1 - p_teorico)**(N - x))
    den = (p_observado**x) * ((1 - p_observado)**(N - x))
    
    lr_stat = -2 * np.log(num / den)
    p_value = 1 - stats.chi2.cdf(lr_stat, df=1)
    
    return lr_stat, p_value, p_observado

lr_95, pval_95, p_obs_95 = kupiec_test(x_95, N, 0.95)
lr_99, pval_99, p_obs_99 = kupiec_test(x_99, N, 0.99)

# -----------------------------------------------------------------------------
# 4. Clasificación según Zonas del Comité de Basilea (para VaR 99%)
# -----------------------------------------------------------------------------
# Basilea define semáforos en 250 días: Verde (0-4), Amarilla (5-9), Roja (10+)
# Escalamos proporcionalmente para N días
excepciones_escaladas_250 = (x_99 / N) * 250

if excepciones_escaladas_250 <= 4:
    zona_basilea = "VERDE (Modelo Aceptado)"
elif excepciones_escaladas_250 <= 9:
    zona_basilea = "AMARILLA (Modelo Bajo Supervisión)"
else:
    zona_basilea = "ROJA (Modelo Rechazado)"

print("="*65)
print(" RESULTADOS DEL BACKTESTING DEL MODELO VaR (PRUEBA DE KUPIEC)")
print("="*65)
print(f"Número de observaciones out-of-sample (N) : {N} días")
print("-" * 65)
print("--- VaR 95% ---")
print(f"Violaciones Esperadas  : {N * 0.05:.1f} ({5.0}%)")
print(f"Violaciones Observadas : {x_95} ({p_obs_95*100:.2f}%)")
print(f"Estadístico LR         : {lr_95:.4f}")
print(f"p-valor (Kupiec)       : {pval_95:.4f} --> {'ACEPTADO (Modelo Calibrado)' if pval_95 > 0.05 else 'RECHAZADO'}")
print("-" * 65)
print("--- VaR 99% ---")
print(f"Violaciones Esperadas  : {N * 0.01:.1f} ({1.0}%)")
print(f"Violaciones Observadas : {x_99} ({p_obs_99*100:.2f}%)")
print(f"Estadístico LR         : {lr_99:.4f}")
print(f"p-valor (Kupiec)       : {pval_99:.4f} --> {'ACEPTADO (Modelo Calibrado)' if pval_99 > 0.05 else 'RECHAZADO'}")
print(f"Clasificación Basilea  : {zona_basilea}")
print("="*65)

# -----------------------------------------------------------------------------
# 5. Visualización del Backtesting
# -----------------------------------------------------------------------------
plt.figure(figsize=(12, 6))
plt.plot(pérdidas_reales, color='black', alpha=0.6, linewidth=1, label='Pérdida Real Diaria (%)')
plt.plot(var_95_series, color='orange', linestyle='--', linewidth=1.5, label='VaR 95% Estimado')
plt.plot(var_99_series, color='red', linestyle='--', linewidth=1.5, label='VaR 99% Estimado')

# Resaltar puntos de violación
plt.scatter(np.where(violaciones_95)[0], pérdidas_reales[violaciones_95], color='orange', s=30, zorder=5, label=f'Violaciones VaR 95% ({x_95})')
plt.scatter(np.where(violaciones_99)[0], pérdidas_reales[violaciones_99], color='red', s=50, marker='x', zorder=6, label=f'Violaciones VaR 99% ({x_99})')

plt.title('Backtesting de Pérdidas de Portafolio vs. VaR (Cópula-GARCH)', fontsize=12)
plt.xlabel('Días de Operación (Out-of-Sample)')
plt.ylabel('Pérdida (%)')
plt.legend(loc='upper right')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()