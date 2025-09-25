def formato_moneda_mx(valor):
    """
    Formatea un número al formato de moneda mexicana
    Ejemplo: 13000 -> "$13,000.00"
    """
    try:
        valor = float(valor)
        if valor == 0:
            return "$0.00"
        return f"${valor:,.2f}"
    except (ValueError, TypeError):
        return "$0.00"