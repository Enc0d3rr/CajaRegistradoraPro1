def formato_moneda_mx(valor, simbolo="$", decimales=2):
    """
    Formatea un número al formato de moneda mexicana
    Ejemplo: 13000 -> "$13,000.00"
    """
    try:
        valor_float = float(valor)
        
        # Formatear correctamente con separadores de miles
        formatted = f"{valor_float:,.{decimales}f}"
        
        # Asegurar el formato mexicano: $1,200.00 (no $1200.00)
        return f"{simbolo}{formatted}"
        
    except (ValueError, TypeError):
        return f"{simbolo}0.00"

# Función adicional para ayudar en las tablas
def aplicar_formato_moneda_tabla(tabla, columnas_moneda):
    """
    Aplica formato de moneda a columnas específicas de una tabla
    """
    for fila in range(tabla.rowCount()):
        for columna in columnas_moneda:
            item = tabla.item(fila, columna)
            if item and item.text().strip():
                try:
                    # Limpiar el texto actual y convertir a número
                    texto_limpio = item.text().replace('$', '').replace(',', '').strip()
                    if texto_limpio:
                        valor = float(texto_limpio)
                        item.setText(formato_moneda_mx(valor))
                except (ValueError, TypeError):
                    pass