import json
import os
import sys
from datetime import datetime
from utils.helpers import formato_moneda_mx

def get_app_directory():
    """
    Obtiene el directorio base de la aplicación.
    Funciona tanto en desarrollo como cuando está compilado a .exe
    """
    if getattr(sys, 'frozen', False):
        # Si está compilado, la ruta es donde está el ejecutable
        return os.path.dirname(sys.executable)
    else:
        # Si está en desarrollo, la ruta es donde está el script
        return os.path.dirname(os.path.abspath(__file__))

def ensure_directory_exists(directory_path):
    """
    Asegura que un directorio exista.
    Si no existe, lo crea.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"✅ Carpeta creada: {directory_path}")
    return directory_path

def generar_ticket(carrito, iva, total=None, metodo_pago="Efectivo", nombre_negocio=None, numero_venta=None):
    """
    Genera un ticket de texto bien alineado y centrado y lo guarda dentro de la carpeta 'tickets/'.
    Devuelve la ruta completa del archivo generado.
    """
    # Obtener directorio base de la aplicación (funciona compilado y desarrollo)
    base_dir = get_app_directory()

    # carpeta donde se guardarán los tickets
    tickets_dir = os.path.join(base_dir, "tickets")
    ensure_directory_exists(tickets_dir)

    # intentar leer nombre del negocio desde config.json si no se proporciona
    if nombre_negocio is None:
        try:
            ruta_cfg = os.path.join(base_dir, "config.json")
            if os.path.exists(ruta_cfg):
                with open(ruta_cfg, "r", encoding="utf-8") as fh:
                    cfg = json.load(fh)
                nombre_negocio = cfg.get("nombre_negocio", "")
        except Exception:
            nombre_negocio = ""

    now_dt = datetime.now()
    timestamp = now_dt.strftime("%Y-%m-%d_%H-%M-%S")
    fecha_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    nombre_archivo = f"ticket_{timestamp}.txt"
    if numero_venta:
        nombre_archivo = f"ticket_{numero_venta:06d}_{timestamp}.txt"
    ruta_archivo = os.path.join(tickets_dir, nombre_archivo)

    # Cálculos
    subtotal = sum(item['precio'] * item['cantidad'] for item in carrito)

    # detectar si 'iva' es tasa o monto
    if iva is None:
        iva_amount = 0.0
        iva_rate = 0.0
    else:
        try:
            iva_val = float(iva)
            if iva_val <= 1:  # lo interpretamos como tasa (ej. 0.18)
                iva_rate = iva_val
                iva_amount = subtotal * iva_rate
            else:  # lo interpretamos como monto
                iva_amount = iva_val
                iva_rate = subtotal and (iva_amount / subtotal) or 0.0
        except Exception:
            iva_amount = 0.0
            iva_rate = 0.0

    total_calc = total if (total is not None) else (subtotal + iva_amount)

    # calcular anchos de columna
    nombres = [item['nombre'] for item in carrito] if carrito else []
    max_name = max([len(n) for n in nombres] + [len("Producto")]) if nombres else len("Producto")
    name_w = min(max(max_name, len("Producto")), 30)   # limitar a 30 chars
    qty_w = max(6, len("Cant."))
    price_w = max(8, len("P/U"))
    subtotal_w = max(10, len("Subtotal"))

    # ancho total y separadores
    padding_between = 4  # espacios entre columnas
    total_width = name_w + qty_w + price_w + subtotal_w + padding_between
    sep_eq = "=" * total_width
    sep_dash = "-" * total_width

    # construir el ticket y guardarlo en tickets/
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.write(sep_eq + "\n")
        if nombre_negocio:
            f.write(nombre_negocio.center(total_width) + "\n")
        f.write("TICKET DE VENTA".center(total_width) + "\n")
        if numero_venta:
            f.write(f"N° Venta: {numero_venta:06d}".center(total_width) + "\n")
        f.write(fecha_str.center(total_width) + "\n")
        f.write(sep_eq + "\n\n")

        # cabecera de columnas
        header = f"{'Producto':<{name_w}}{'':2}{'Cant.':>{qty_w}}{'':2}{'P/U':>{price_w}}{'':2}{'Subtotal':>{subtotal_w}}"
        f.write(header + "\n")
        f.write(sep_dash + "\n")

        # ✅ CORREGIDO - filas de productos (SOLO el bucle, sin código fuera)
        for item in carrito:
            nombre = item['nombre'][:name_w]  # truncar si demasiado largo
            cantidad = int(item['cantidad'])
            precio = float(item['precio'])
            sub_item = precio * cantidad
            
            # Línea corregida
            line = f"{nombre:<{name_w}}{'':2}{cantidad:>{qty_w}}{'':2}{formato_moneda_mx(precio).replace('$', ''):>{price_w}}{'':2}{formato_moneda_mx(sub_item).replace('$', ''):>{subtotal_w}}"
            f.write(line + "\n")

        f.write("\n")
        f.write(sep_dash + "\n")

        # totales alineados a la derecha
        label_w = total_width - 12  # espacio reservado para la cifra final
        
        f.write(f"{'Subtotal:':>{label_w}}{formato_moneda_mx(subtotal).replace('$', ''):>12}\n")
        if iva_rate > 0:
            f.write(f"{'IVA (' + str(int(round(iva_rate*100))) + '%):':>{label_w}}{formato_moneda_mx(iva_amount).replace('$', ''):>12}\n")
        f.write(f"{'TOTAL:':>{label_w}}{formato_moneda_mx(total_calc).replace('$', ''):>12}\n")
        
        # Nueva línea para método de pago
        f.write(f"{'Método de pago:':>{label_w}}{metodo_pago:>12}\n")
        
        f.write(sep_eq + "\n\n")

        # footer centrado y separación final
        f.write("Gracias por su compra".center(total_width) + "\n")
        f.write(sep_eq + "\n")

    ruta_abs = os.path.abspath(ruta_archivo)
    print(f"✅ Ticket guardado en: {ruta_abs}")
    return ruta_abs