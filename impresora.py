import os
from dotenv import load_dotenv

load_dotenv()

PRINTER_ENABLED = os.getenv("PRINTER_ENABLED", "true").lower() == "true"
PRINTER_NAME = os.getenv("PRINTER_NAME", "POS-58")
ANCHO = 32

ESC = b'\x1b'
GS = b'\x1d'
CMD_INIT = ESC + b'@'
CMD_ALIGN_CENTER = ESC + b'a\x01'
CMD_ALIGN_LEFT = ESC + b'a\x00'
CMD_BOLD_ON = ESC + b'E\x01'
CMD_BOLD_OFF = ESC + b'E\x00'
CMD_TAMANO_NORMAL = GS + b'!\x00'
CMD_TAMANO_DOBLE_ALTO = GS + b'!\x01'
CMD_CORTE_PARCIAL = GS + b'V\x01'


def _encode(texto):
    return texto.encode("cp437", errors="replace")


def _separador(caracter="="):
    return _encode(caracter * ANCHO + "\n")


def _linea(texto):
    return _encode(texto + "\n")


def _formato_producto(nombre, cantidad, subtotal):
    izquierda = f"{cantidad}x {nombre}"
    derecha = f"${subtotal:.2f}"
    espacio = ANCHO - len(izquierda) - len(derecha)
    if espacio < 1:
        izquierda = izquierda[:ANCHO - len(derecha) - 1]
        espacio = 1
    return _encode(izquierda + " " * espacio + derecha + "\n")


def _formato_total(total):
    izquierda = "TOTAL:"
    derecha = f"${total:.2f}"
    espacio = ANCHO - len(izquierda) - len(derecha)
    return _encode(izquierda + " " * max(espacio, 1) + derecha + "\n")


def _enviar_a_impresora(datos_bytes):
    import win32print
    handle = win32print.OpenPrinter(PRINTER_NAME)
    try:
        win32print.StartDocPrinter(handle, 1, ("Ticket IGJ", None, "RAW"))
        win32print.StartPagePrinter(handle)
        win32print.WritePrinter(handle, datos_bytes)
        win32print.EndPagePrinter(handle)
        win32print.EndDocPrinter(handle)
    finally:
        win32print.ClosePrinter(handle)


def construir_datos_reimpresion(fila_pedido, cursor):
    id_pedido = fila_pedido[0]
    nombre_cliente = fila_pedido[1] or "Cliente"
    producto_texto = fila_pedido[2] or ""
    fecha = fila_pedido[3]
    hora = fila_pedido[4]
    total = float(fila_pedido[5] or 0)
    metodo_pago = fila_pedido[6] or "efectivo"

    productos = []
    for item in producto_texto.split(", "):
        partes = item.split("x ", 1)
        if len(partes) == 2 and partes[0].strip().isdigit():
            cantidad = int(partes[0].strip())
            nombre = partes[1].strip()
            cursor.execute(
                "SELECT precio FROM Productos WHERE nombre = %s",
                (nombre,)
            )
            resultado = cursor.fetchone()
            precio_unitario = float(resultado[0]) if resultado else 0.0
            productos.append({
                "nombre": nombre,
                "cantidad": cantidad,
                "subtotal": cantidad * precio_unitario
            })

    fecha_str = fecha.strftime("%d/%m/%Y") if hasattr(fecha, "strftime") else str(fecha)
    hora_str = str(hora)[:5] if hora else "--:--"

    return {
        "id_pedido": id_pedido,
        "nombre_cliente": nombre_cliente,
        "fecha": fecha_str,
        "hora": hora_str,
        "productos": productos,
        "total": total,
        "metodo_pago": metodo_pago
    }


def imprimir_ticket(datos):
    if not PRINTER_ENABLED:
        return False

    ticket = bytearray()

    ticket += CMD_INIT

    ticket += CMD_ALIGN_CENTER
    ticket += _separador("=")
    ticket += CMD_BOLD_ON + CMD_TAMANO_DOBLE_ALTO
    ticket += _linea("CAFETERIA IGJ")
    ticket += CMD_BOLD_OFF + CMD_TAMANO_NORMAL
    ticket += _separador("=")

    ticket += CMD_ALIGN_LEFT
    ticket += _linea(f"Pedido: #{datos['id_pedido']}")
    ticket += _linea(f"Cliente: {datos['nombre_cliente']}")
    ticket += _linea(f"Fecha: {datos['fecha']}")
    ticket += _linea(f"Hora:  {datos['hora']}")
    ticket += _separador("-")

    for prod in datos["productos"]:
        ticket += _formato_producto(
            prod["nombre"],
            prod["cantidad"],
            prod["subtotal"]
        )

    ticket += _separador("-")

    ticket += CMD_BOLD_ON + CMD_TAMANO_DOBLE_ALTO
    ticket += _formato_total(datos["total"])
    ticket += CMD_BOLD_OFF + CMD_TAMANO_NORMAL

    metodo = "Efectivo" if datos["metodo_pago"] == "efectivo" else "Tarjeta"
    ticket += _linea(f"Pago: {metodo}")

    ticket += _separador("=")
    ticket += CMD_ALIGN_CENTER
    ticket += _linea("Gracias por tu compra!")
    ticket += _linea("Te esperamos pronto")
    ticket += b'\n\n\n'

    ticket += CMD_CORTE_PARCIAL

    _enviar_a_impresora(bytes(ticket))
    return True
