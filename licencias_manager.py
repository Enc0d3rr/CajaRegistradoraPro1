# licencias_manager.py - VERSIÓN SOLO PREMIUM
import json
import os
import hashlib
import uuid
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import base64

class LicenseManager:
    def __init__(self, app_name="CajaRegistradoraPro"):
        self.app_name = app_name
        self.license_file = "licencia.lic"
        self.encryption_key = self._generate_encryption_key()
        
    def _get_hardware_id(self):
        """Obtiene un ID único del hardware"""
        try:
            return str(uuid.getnode())
        except:
            return hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16]
    
    def _generate_encryption_key(self):
        """Genera clave de encriptación basada en hardware"""
        hardware_id = self._get_hardware_id()
        return hashlib.sha256(hardware_id.encode()).digest()[:32]
    
    def _encrypt_data(self, data):
        """Encripta datos de la licencia"""
        try:
            fernet = Fernet(base64.urlsafe_b64encode(self.encryption_key))
            encrypted_data = fernet.encrypt(json.dumps(data).encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            print(f"Error encriptando: {e}")
            return None
    
    def _decrypt_data(self, encrypted_data):
        """Desencripta datos de la licencia"""
        try:
            fernet = Fernet(base64.urlsafe_b64encode(self.encryption_key))
            decrypted_data = fernet.decrypt(base64.urlsafe_b64decode(encrypted_data))
            return json.loads(decrypted_data.decode())
        except Exception as e:
            print(f"Error desencriptando: {e}")
            return None
    
    def _guardar_licencia(self, licencia_data):
        """Guarda la licencia encriptada"""
        try:
            encrypted_data = self._encrypt_data(licencia_data)
            if encrypted_data:
                with open(self.license_file, 'w') as f:
                    f.write(encrypted_data)
                return True
        except Exception as e:
            print(f"Error guardando licencia: {e}")
        return False
    
    def _cargar_licencia(self):
        """Carga y desencripta la licencia"""
        try:
            if os.path.exists(self.license_file):
                with open(self.license_file, 'r') as f:
                    encrypted_data = f.read().strip()
                return self._decrypt_data(encrypted_data)
        except Exception as e:
            print(f"Error cargando licencia: {e}")
        return None

    def validar_licencia(self):
        """Valida si la licencia premium es válida - NO PRUEBAS AUTOMÁTICAS"""
        # ❌ NO activar prueba automática si no existe licencia
        if not os.path.exists(self.license_file):
            print("❌ No existe licencia. Software no activado.")
            return False
        
        try:
            licencia_data = self._cargar_licencia()
            
            if not licencia_data:
                print("❌ Licencia corrupta.")
                return False
            
            if not licencia_data.get('activa', False):
                print("❌ Licencia inactiva.")
                return False
            
            # Verificar fecha de expiración
            fecha_expiracion = datetime.fromisoformat(licencia_data['fecha_expiracion'])
            if datetime.now() > fecha_expiracion:
                print("❌ Licencia expirada.")
                return False
                
            # Verificar hardware
            if licencia_data.get('hardware_id') != self._get_hardware_id():
                print("❌ Licencia no válida para este equipo.")
                return False
                
            # Calcular días restantes
            dias_restantes = (fecha_expiracion - datetime.now()).days
            licencia_data['dias_restantes'] = max(0, dias_restantes)
            self._guardar_licencia(licencia_data)
            
            print(f"✅ Licencia premium válida. Días restantes: {dias_restantes}")
            return True
            
        except Exception as e:
            print(f"❌ Error validando licencia: {e}")
            return False  # ❌ NO activar prueba en error

    def obtener_info_licencia(self):
        """Obtiene información completa de la licencia"""
        try:
            if not os.path.exists(self.license_file):
                return {
                    'tipo': 'no_activada',
                    'dias_restantes': 0,
                    'estado': 'no_activada',
                    'mensaje': 'Licencia no activada'
                }
            
            licencia_data = self._cargar_licencia()
            if not licencia_data:
                return {
                    'tipo': 'corrupta',
                    'dias_restantes': 0,
                    'estado': 'error',
                    'mensaje': 'Error en licencia'
                }
            
            # Calcular días restantes
            dias_restantes = 0
            estado = 'inactiva'
            
            if 'fecha_expiracion' in licencia_data:
                fecha_expiracion = datetime.fromisoformat(licencia_data['fecha_expiracion'])
                dias_restantes = (fecha_expiracion - datetime.now()).days
                estado = 'activa' if dias_restantes > 0 else 'expirada'
            
            return {
                'tipo': licencia_data.get('tipo', 'desconocido'),
                'dias_restantes': max(0, dias_restantes),
                'fecha_expiracion': licencia_data.get('fecha_expiracion', ''),
                'estado': estado,
                'activa': licencia_data.get('activa', False),
                'mensaje': 'Licencia premium' if estado == 'activa' else 'Licencia requerida'
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo info licencia: {e}")
            return {
                'tipo': 'error',
                'dias_restantes': 0,
                'estado': 'error',
                'mensaje': 'Error al cargar licencia'
            }
    
    def activar_licencia_paga(self, codigo_activacion):
        """Activa licencia premium"""
        # Validación del código
        if len(codigo_activacion) == 16 and codigo_activacion.startswith("CRP"):
            licencia_data = {
                'tipo': 'paga',
                'fecha_activacion': datetime.now().isoformat(),
                'fecha_expiracion': (datetime.now() + timedelta(days=30)).isoformat(),  # 1 mes
                'activa': True,
                'hardware_id': self._get_hardware_id(),
                'codigo_activacion': codigo_activacion
            }
            
            if self._guardar_licencia(licencia_data):
                print("✅ Licencia premium activada")
                return True
        
        print("❌ Código de activación inválido")
        return False

    def mostrar_dialogo_activacion(self):
        """Muestra el diálogo de activación premium"""
        try:
            from dialogo_activacion import DialogoActivacion
            print("🎫 Abriendo diálogo de activación premium...")
            
            dialogo = DialogoActivacion(self, None)
            resultado = dialogo.exec()
            
            print(f"📝 Diálogo cerrado. Resultado: {resultado}")
            return resultado
            
        except Exception as e:
            print(f"❌ Error mostrando diálogo: {e}")
            return 0

# Prueba del sistema
if __name__ == "__main__":
    print("🧪 Probando LicenseManager (Versión Premium)...")
    
    manager = LicenseManager()
    
    # Test: Info sin licencia
    print("\n1. Estado sin licencia:")
    info = manager.obtener_info_licencia()
    print(f"   {info}")
    
    # Test: Validar sin licencia (debe retornar False)
    print("\n2. Validando sin licencia...")
    if manager.validar_licencia():
        print("   ✅ Licencia válida")
    else:
        print("   ❌ Licencia no válida (comportamiento esperado)")
    
    print("\n🎉 Prueba completada!")