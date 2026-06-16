import pandas as pd

productos = pd.read_excel('Dsetprueba.xlsx', sheet_name='productos')
pedidos = pd.read_excel('Dsetprueba.xlsx', sheet_name='pedidos')
lineas_pedidos = pd.read_excel('Dsetprueba.xlsx', sheet_name='lineas_pedido')
facturas = pd.read_excel('Dsetprueba.xlsx', sheet_name='facturas')

#totates por pedido
datos = pd.merge(
    lineas_pedidos,
    productos,
    on='producto_id',
    how='left'
)

datos['base']= (
    datos['precio_unitario'] * datos['cantidad']*(1-datos['descuento'])
)
datos['iva'] = datos['base'] * datos['iva'] /100
datos['total'] = datos['base'] + datos['iva']

totales_pedidos = datos.groupby('pedido_id').agg({'base':'sum', 'iva':'sum', 'total':'sum'}).reset_index()

totales_pedidos = totales_pedidos.round(2)
print("*****Totales por pedido*****")
print(totales_pedidos)

#quiebre de stock
demanda = lineas_pedidos.groupby('producto_id').agg({'cantidad':'sum'}).reset_index()

stock = pd.merge(
    demanda,
    productos,
    on='producto_id',
    how='left'
)

faltantes = stock[stock['cantidad'] > stock['stock_actual']].copy()

faltantes['faltante'] = faltantes['cantidad'] - faltantes['stock_actual']
print("*****Faltantes de stock*****")
print(faltantes[['producto_id', 'nombre', 'cantidad', 'stock_actual', 'faltante']])

#cartera por cliente
facturas['saldo'] = facturas['monto'] - facturas['pagado']

facturas_pulicadas  = facturas[facturas['estado'] == 'publicada']

facturas_pendientes = facturas_pulicadas[facturas_pulicadas['saldo'] > 0]
cartera_clientes = facturas_pendientes.groupby('cliente')['saldo'].sum()

print("*****Cartera por cliente*****")
print(cartera_clientes)

print("***** Total *****")
print(cartera_clientes.sum())

#opcional 

facturas_pendientes['vencimiento']= pd.to_datetime(facturas_pendientes['vencimiento'])

fecha_referencia = pd.Timestamp('2026-06-16')
facturas_pendientes['dias'] = (fecha_referencia - facturas_pendientes['vencimiento']).dt.days

def clasificar_vencimiento(dias):
    if dias < 0:
        return 'por vencer'
    elif dias <= 30:
        return '0-30 dias'
    elif dias <= 60:
        return '31-60 dias'
    else:
        return 'mas de 90 dias'
    
facturas_pendientes['categoria'] = facturas_pendientes['dias'].apply(clasificar_vencimiento)
cartera_vencimiento = facturas_pendientes.groupby('categoria')['saldo'].sum()
print("*****Cartera por vencimiento*****")
print(cartera_vencimiento)