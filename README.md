# Proyecto Python: Análisis de Embudo de Conversión y Tiempos de Compra con Pandas

Este repositorio contiene un proyecto práctico desarrollado en Python utilizando la librería **Pandas** para modelar e inspeccionar el comportamiento de los usuarios a través de un embudo de conversión (*Conversion Funnel*) en una plataforma de comercio electrónico. El script consolida múltiples fuentes de datos transaccionales mediante uniones lógicas por la izquierda (*Left Joins*), calcula de manera porcentual las tasas de abandono en cada etapa crítica del flujo y analiza la eficiencia del sistema mediante el cálculo de marcas de tiempo medias del ciclo de compra completo.

---

## Código Python del Proyecto

El programa unifica los sets de datos distribuidos y extrae métricas de abandono corporativas desde la visita inicial hasta la confirmación del pago:

```python
import pandas as pd

# --- 1. Ingesta de Datos y Parseo de Fechas ---
visits = pd.read_csv('visits.csv', parse_dates=[1])
cart = pd.read_csv('cart.csv', parse_dates=[1])
checkout = pd.read_csv('checkout.csv', parse_dates=[1])
purchase = pd.read_csv('purchase.csv', parse_dates=[1])

# --- 2. Análisis del Primer Paso: Visita a Carrito ---
visits_to_cart = visits.merge(cart, how="left")
visits_total_len = len(visits_to_cart)
visits_is_null = len(visits_to_cart[visits_to_cart.cart_time.isnull()])

# --- 3. Análisis de Deserción en Etapas Intermedias ---
# Tasa de abandono para usuarios que añadieron productos al carrito pero no compraron
cart_to_purchase = cart.merge(purchase, how="left")
no_purchase_rate = cart_to_purchase.purchase_time.isnull().mean() * 100
print("Tasa de abandono en carrito: " + str(round(no_purchase_rate, 2)) + "%")

# Tasa de abandono para usuarios que iniciaron el proceso de checkout
cart_checkout = cart.merge(checkout, how='left')
checkout_purchase = cart_checkout.merge(purchase, how='left')
no_purchase_after_checkout = checkout_purchase.purchase_time.isnull().mean() * 100
print("Tasa de abandono en checkout: " + str(round(no_purchase_after_checkout, 2)) + "%")

# --- 4. Consolidación de la Lista Maestra General ---
all_data = visits_to_cart.merge(cart_checkout, how='left').merge(purchase, how='left')
print(all_data.head(5))

# --- 5. Análisis del Ciclo de Tiempo de Conversión ---
# Cálculo de la diferencia temporal (Timedelta) entre la visita y la compra
all_data["time_to_purchase"] = (all_data["purchase_time"] - all_data["visit_time"])
average_purchase_time = all_data['time_to_purchase'].mean()

print("Tiempo promedio transcurrido hasta la compra: " + str(average_purchase_time))

```

---

## Estructura de Datos e Interpretación del Embudo

El procesamiento unifica las tablas mediante uniones relacionales externas por la izquierda (`how="left"`). Esto preserva el registro de la etapa anterior y rellena con valores nulos (`NaN` o `NaT`) si el usuario abandonó el flujo:

### 1. Modelo de Intersección de Datos Coincidentes

Cuando un cliente progresa a lo largo de la plataforma, sus registros cronológicos se alinean en la misma fila del DataFrame maestro. Si deserta, las columnas posteriores se truncan automáticamente:

| user_id | visit_time | cart_time | checkout_time | purchase_time | Diagnóstico del Perfil |
| --- | --- | --- | --- | --- | --- |
| `943647ef...` | 2017-04-07 15:14 | NaT | NaT | NaT | Abandono tras visitar la página home. |
| `0c3a3dd0...` | 2017-01-26 14:24 | 2017-01-26 15:08 | NaT | NaT | Añadió al carrito pero no inició checkout. |
| `a84327ff...` | 2017-02-27 11:25 | 2017-02-27 12:00 | 2017-02-27 12:15 | 2017-02-27 12:43 | **Conversión Exitosa (Ciclo Completo)** |

### 2. Métricas de Rendimiento del Negocio

Al auditar los registros huérfanos que contienen valores nulos, el motor calcula los porcentajes de deserción del embudo:

* **Abandono en Carrito:** Porcentaje de usuarios que colocaron artículos en su carrito pero salieron de la tienda antes de registrar una intención de pago.
* **Abandono en Checkout:** Usuarios con intenciones de compra avanzadas que abandonaron el formulario final en la pasarela de pago.
* **Latencia del Ciclo Temporal:** Promedio de horas, minutos y segundos que le toma a un cliente madurar su decisión desde que ingresa al sitio web hasta que el pago es procesado de forma conforme.

---

## Conceptos Técnicos Aplicados

* **Método `.merge(how="left")**`: Operación relacional que combina dos DataFrames basándose en las columnas comunes (como `user_id`). El modo por la izquierda garantiza la conservación total del volumen de datos de la primera colección, permitiendo cuantificar la pérdida de registros subsiguientes mediante campos nulos.
* **Parseo de Fechas Extrínseco (`parse_dates`)**: Instrucción inyectada durante la lectura del CSV que transforma las cadenas de texto con marcas cronológicas en objetos nativos `datetime64` de Pandas, habilitando operaciones de cálculo aritmético sobre el tiempo.
* **Operaciones con Series Temporales (*Timedeltas*)**: La sustracción directa de objetos datetime (`purchase_time - visit_time`) genera una nueva serie de tipo delta temporal, permitiendo aplicar métodos estadísticos de agregación (como `.mean()`) sobre diferencias de tiempo absolutas.

```
