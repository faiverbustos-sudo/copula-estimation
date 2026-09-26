# Implementación en Python: Estimación por Pseudo-Máxima Verosimilitud (CML) Clayton Copula

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