#!/bin/bash
echo "📦 PREPARANDO PROYECTO PARA COMPILACIÓN EN WINDOWS"
echo "=================================================="

# Limpiar archivos temporales
echo "🧹 Limpiando archivos temporales..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.log" -delete

# Crear lista de archivos esenciales
echo "📋 Creando lista de archivos..."
cat > lista_archivos.txt << 'EOF'
auth_manager.py
backup_manager.py
caja_registradora.py
cash_close_manager.py
category_manager.py
config_manager.py
config_panel.py
database.py
export_dialog.py
inventory_manager.py
password_dialog.py
paths.py
sales_history.py
themes.py
ticket_generator.py
user_manager.py
compilador.bat
requirements.txt
icono.ico
email_system/
licenses/
utils/
data/
EOF

# Crear zip
echo "🗜️ Creando archivo comprimido..."
zip -r caja_registradora_para_windows.zip -@ < lista_archivos.txt

# Limpiar
rm lista_archivos.txt

echo ""
echo "✅ ¡PROYECTO LISTO PARA WINDOWS!"
echo "📍 Archivo: caja_registradora_para_windows.zip"
echo ""
echo "📝 SIGUIENTES PASOS:"
echo "1. Copiar ZIP a Windows"
echo "2. Descomprimir" 
echo "3. Ejecutar 'compilar_protegido.bat'"
echo "4. ¡Obtener .exe protegido!"
