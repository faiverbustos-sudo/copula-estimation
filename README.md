# 1. Implementación en Python: Estimación por Pseudo-Máxima Verosimilitud (CML) - Clayton Copula

Script: clayton-copula-brent-exchange-rate.py

En el contexto macroeconómico colombiano, una de las aplicaciones más relevantes de las cópulas econométricas es el análisis de dependencia no lineal entre el precio del petróleo Brent y la tasa de cambio USD/COP.

Dado que Colombia es una economía primario-exportadora, una caída severa en los precios del petróleo suele desencadenar depreciaciones aceleradas del peso colombiano. Esta relación presenta dependencia asimétrica en las colas, donde los eventos extremos negativos en el petróleo impactan con mayor intensidad al tipo de cambio que los aumentos de precio.

## Interpretación de Resultados

Transformación a Rangos: Mediante la función de distribución empírica (rankdata), se eliminan los sesgos o distribuciones no normales de los retornos individuales de cada activo.

Parámetro $\theta$: Representa la fuerza de asociación entre las variables. Un valor alto de $\theta$ indica un acoplamiento fuerte en momentos de estrés. Parámetro de acoplamiento de la cópula de Clayton ($\theta > 0$): Confirma la presencia de una estructura de dependencia no lineal con asimetría enfocada en la cola conjunta inferior.

Tau de Kendall ($\tau$): Correlación no paramétrica basada en concordancia de rangos. Muestra una dependencia global moderada a alta en condiciones normales de mercado entre el comportamiento del Brent y el tipo de cambio.

Coeficiente de Cola Inferior ($\lambda_L$): Mide la probabilidad condicional de observar una depreciación extrema del Peso Colombiano dado que el barril de Brent sufrió una caída en el percentil más bajo. Ejemplo: Probabilidad condicional de ocurrencia simultánea de eventos extremos (55.83%): Resultado clave de riesgo: Ante un colapso extremo en el precio del petróleo (percentiles más bajos), existe un 55.83% de probabilidad de observar una depreciación extrema simultánea en la tasa USD/COP.

## Implicaciones para el Análisis Económico y Financiero

Subestimación del Riesgo bajo Normalidad (Efecto Contagio):Un modelo tradicional basado en matriz de varianzas-covarianzas o correlación lineal de Pearson asumiría que la relación es constante en todo momento. La cópula demuestra que durante mercados tranquilos la correlación es moderada ($\tau \approx 0.37$), pero en momentos de estrés petrolero la dependencia salta al $55.83\%$.

Gestión de Portafolio y Coberturas Cambiarias:Para un inversionista o tesorería corporativa en Colombia, esto significa que las coberturas tradicionales pierden efectividad cuando más se necesitan. En escenarios de pánico petrolero, los activos denominados en pesos se desprecian a un ritmo acelerado debido al fuerte acoplamiento estructural.

Pruebas de Estrés y Value-at-Risk (VaR):El cálculo del Value at Risk (VaR) del presupuesto nacional o de entidades financieras expuestas a hidrocarburos que use distribuciones Gaussianas subestimará sustancialmente las pérdidas en las colas. La cópula de Clayton captura con mayor precisión las necesidades de capital de reserva para shocks fiscales.

# 2. Estimación por Pseudo-Máxima Verosimilitud (CML) - Clayton Copula con filtrado previo ARMA-GARCH

Script: arma-garch-clayton-copula-brent-exchange-rate.py

En series de tiempo financieras como el Brent y la tasa USD/COP, los retornos presentan heterocedasticidad condicional (agrupamiento de volatilidad / volatility clustering) y autocorrelación. Si aplicamos la cópula directamente sobre los retornos brutos, se violaría el supuesto de independencia e idéntica distribución (i.i.d.) de los residuos.

Para resolver esto, se utiliza la metodología Copula-GARCH:

Filtrado Marginal: Se ajusta un modelo ARMA(p,q)-GARCH(p,q) a cada serie para remover la media y la volatilidad condicional $\sigma_t$.

Extracción de Residuos Estandarizados: Se obtienen los residuos limpios $z_{t} = \frac{\epsilon_{t}}{\sigma_{t}}$.

Transformación a Uniformes $U(0,1)$: Mediante la Transformación Integral de la Probabilidad (PIT) usando la CDF empírica o t-Student.

Estimación de la Cópula: Se ajusta la cópula sobre la estructura de dependencia de los residuos i.i.d.

## ¿Qué aporta el filtrado GARCH al análisis?

Aislamiento del Sesgo por Volatilidad: Al remover el volatility clustering, evitamos atribuir erróneamente la alta correlación en periodos de turbulencia simplemente a que las varianzas individuales aumentaron.

Dependencia Pura en los Shocks: El parámetro de la cópula ($\theta$) resultante refleja únicamente la interconexión estructural de los shocks exógenos, sin la distorsión del pasado de volatilidad del mercado.

Simulación Monte Carlo de Riesgo (VaR): Con este esquema de dos pasos es posible simular escenarios futuros: primero se simulan los residuos mediante la cópula y luego se les reinyecta la volatilidad condicional pronosticada por el modelo GARCH.

## Interpretación de una simulación con ARMA-GARCH


### RESUMEN DEL FILTRADO GARCH(1,1)

Brent  - Omega: 0.0656, Alpha: 0.1203, Beta: 0.8068
USDCOP - Omega: 0.2254, Alpha: 0.1725, Beta: 0.7664


### RESULTADOS CÓPULA CLAYTON SOBRE RESIDUOS GARCH

Parámetro Theta (θ)  : 1.0831

Tau de Kendall (τ)   : 0.3513

Dependencia Cola (λ_L): 0.5273

### Interpretación econométrica

La interpretación del resultado se divide en dos niveles: la dinámica de volatilidad individual de cada activo (GARCH) y la estructura de interdependencia pura entre sus shocks (Cópula Clayton).

### 1. Filtrado GARCH(1,1): Dinámica de Volatilidad Individual

El modelo especifica la varianza condicional como:

$$\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$

Constante ($\omega$): Brent = 0.0656 | USD/COP = 0.2254
| Significado econométrico: Nivel base incondicional de la varianza. El USD/COP presenta una variabilidad estructural base más alta.

Reacción ($\alpha$): Brent = 0.1203 | USD/COP = 0.1725 | Significado econométrico: Sensibilidad ante nuevos shocks (efecto ARCH). El tipo de cambio reacciona con mayor brusquedad a la llegada de nuevas noticias diarias que el Brent.

Memoria ($\beta$): Brent = 0.8068 | USD/COP = 0.7664 | Significado econométrico: Persistencia de la volatilidad pasada (efecto GARCH). En el Brent, la turbulencia pasada tarda ligeramente más en disiparse.

Persistencia ($\alpha + \beta$): Brent = 0.9271 | USD/COP = 0.9389 | Significado econométrico: La suma es menor a 1 (proceso estacionario). Cerca de $0.93$ en ambos casos indica alta agrupación de volatilidad (volatility clustering): periodos de alta volatilidad son seguidos por alta volatilidad.

### 2. Cópula Clayton sobre Residuos: Dependencia Pura de Shocks

Al remover la volatilidad condicional mediante el GARCH, se trabajó con los residuos estandarizados e independientes $z_t$. La cópula mide la relación limpia entre los impactos no anticipados.

Parámetro Theta ($\theta = 1.0831$): Confirma la presencia de una estructura de dependencia no lineal orientada a la cola inferior, incluso tras aislar la volatilidad de cada mercado.

Tau de Kendall ($\tau = 0.3513$): Existe una correlación de rangos limpia del $35.13\%$ entre los shocks inesperados del petróleo y el tipo de cambio.

Dependencia en Cola Inferior ($\lambda_L = 0.5273$): $$\lambda_L = 2^{-1/\theta} = 2^{-1/1.0831} \approx 0.5273$$

Conclusión clave: Ante un choque exógeno extremo en el precio del petróleo (caída súbita en el percentil más bajo), existe un $52.73\%$ de probabilidad de que el peso colombiano sufra una depreciación extrema simultánea ese mismo día.

### 3. Comparación: Datos Brutos vs. Residuos GARCH

Al comparar esta estimación con el ejercicio inicial (sobre retornos sin filtrar):

Sin GARCH: $\lambda_L = 0.5583$ ($55.83\%$)

Con GARCH: $\lambda_L = 0.5273$ ($52.73\%$)

La ligera reducción (~$3.1\%$) demuestra que una pequeña parte de la co-movilidad extrema inicial se debía simplemente a que ambos mercados estaban agitados al mismo tiempo (volatilidad simultánea). Sin embargo, el $52.73\%$ restante es dependencia estructural pura, lo que ratifica que el riesgo de colapso conjunto por transmisión de pánico petrolero hacia el USD/COP en Colombia es real y no un espejismo de la varianza.


# Dependencias de Python 

Instale las dependencias de Python para ejecutar estos scripts con el siguiente comando Python:

pip install arch numpy pandas scipy matplotlib