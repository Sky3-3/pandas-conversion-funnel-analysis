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
