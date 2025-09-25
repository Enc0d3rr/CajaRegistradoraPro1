from licencias_manager import LicenseManager

def test_licencias():
    print("🧪 Probando sistema de licencias...")
    
    manager = LicenseManager()
    
    # Test 1: Validar licencia (debería activar prueba)
    print("\n1. Validando licencia inicial...")
    if manager.validar_licencia():
        info = manager.obtener_info_licencia()
        print(f"   ✅ Licencia activa: {info}")
    else:
        print("   ❌ Falló la validación")
    
    # Test 2: Intentar activar licencia paga
    print("\n2. Probando activación paga...")
    if manager.activar_licencia_paga("CRP1234567890123"):  # Código válido
        print("   ✅ Licencia pagada activada")
    else:
        print("   ❌ Código inválido (esperado)")
    
    # Test 3: Ver info final
    print("\n3. Información final de licencia:")
    info = manager.obtener_info_licencia()
    for key, value in info.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    test_licencias()