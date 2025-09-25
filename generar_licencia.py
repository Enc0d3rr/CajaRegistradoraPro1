import random
import string

def generar_codigo_licencia():
    prefix = "CRP"
    random_digits = ''.join(random.choices(string.digits, k=13))
    return prefix + random_digits

# Ejemplo de uso:
print(generar_codigo_licencia())