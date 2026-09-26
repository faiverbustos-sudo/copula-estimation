# Implementación en Python: Estimación por Pseudo-Máxima Verosimilitud (CML)

En el contexto macroeconómico colombiano, una de las aplicaciones más relevantes de las cópulas econométricas es el análisis de dependencia no lineal entre el precio del petróleo Brent y la tasa de cambio USD/COP.

Dado que Colombia es una economía primario-exportadora, una caída severa en los precios del petróleo suele desencadenar depreciaciones aceleradas del peso colombiano. Esta relación presenta dependencia asimétrica en las colas, donde los eventos extremos negativos en el petróleo impactan con mayor intensidad al tipo de cambio que los aumentos de precio.

## Interpretación de Resultados

Transformación a Rangos: Mediante la función de distribución empírica (rankdata), se eliminan los sesgos o distribuciones no normales de los retornos individuales de cada activo.

Parámetro $\theta$: Representa la fuerza de asociación entre las variables. Un valor alto de $\theta$ indica un acoplamiento fuerte en momentos de estrés.

Coeficiente de Cola Inferior ($\lambda_L$): Mide la probabilidad condicional de observar una depreciación extrema del Peso Colombiano dado que el barril de Brent sufrió una caída en el percentil más bajo.

