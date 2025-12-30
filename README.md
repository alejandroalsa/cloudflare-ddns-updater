# Cloudflare DDNS Updater

Actualiza automáticamente los registros DNS con tu IP pública.

## 🚀 Características

- Actualización automática de registros DNS A en Cloudflare
- Detección inteligente de cambios de IP (solo actualiza cuando es necesario)
- Soporte para múltiples dominios y zonas con diferentes tokens
- Servicio de IP pública configurable
- Notificaciones por email cuando cambia la IP
- Logging detallado de todas las operaciones
- Configuración mediante archivos `.env` y JSON
- Arquitectura modular y escalable
- Diseñado para ejecutarse como servicio systemd o cron job
- Mínimas dependencias

## 📁 Estructura del Proyecto

```
cloudflare-ddns-updater/
├── LICENSE                         # Licencia del proyecto (MIT)
├── README.md                       # Documentación principal
├── .gitignore                      # Archivos ignorados por Git
└── src
    ├── cloudflare-ddns.py          # Script principal del DDNS
    ├── send_email.py               # Envío de notificaciones por email
    ├── config
    │   ├── config.json             # Configuración real
    │   └── config.json.example     # Ejemplo de configuración
    ├── service
    │   ├── cloudflare-ddns.service         # Servicio systemd
    │   └── cloudflare-ddns.service.example # Plantilla de ejemplo
    └── templates
        └── email.html              # Plantilla HTML para emails
```

## 📋 Requisitos

- Python 3.7 o superior
- Cuenta de Cloudflare con acceso a la API
- Token de API de Cloudflare con permisos de edición de DNS

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/alejandroalsa/cloudflare-ddns-updater.git
cd cloudflare-ddns-updater
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
nano .env
```

### 3. Configurar dominios

```bash
cp src/config/config.json.example src/config/config.json
nano src/config/config.json
```

## ☁️ Obtener credenciales de Cloudflare

### 1. Token de API

1. Accede a [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Ve a **My Profile** → **API Tokens**
3. Crea un nuevo token con estos permisos:
   - **Zone.DNS:Edit** (obligatorio)
   - **Zone.Zone:Read** (recomendado)
4. Selecciona las zonas específicas o todas las zonas
5. Copia el token generado

### 2. Zone ID

1. En el Dashboard de Cloudflare, selecciona tu dominio
2. Desplázate a la sección **API** en la barra lateral derecha
3. Copia el **Zone ID**

## 🏃 Uso

### Ejecución manual (una vez)

```bash
python3 src/cloudflare-ddns.py
```

O desde la raíz del proyecto:

```bash
cd cloudflare-ddns-updater
python3 src/cloudflare-ddns.py
```

### Modo verbose (debug)

```bash
python3 src/cloudflare-ddns.py -v
```

## 🔄 Configuración como servicio

### Ejecutar como servicio systemd (recomendado para producción)

1. Copia el archivo de servicio:

```bash
sudo cp src/service/cloudflare-ddns.service /etc/systemd/system/
```

1. Edita las rutas y valores en el archivo de servicio según tu instalación:

```bash
sudo nano /etc/systemd/system/cloudflare-ddns.service
```

1. Habilita e inicia el servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl enable cloudflare-ddns
sudo systemctl start cloudflare-ddns
```

1. Verifica el estado:

```bash
sudo systemctl status cloudflare-ddns
```

1. Ver logs del servicio:

```bash
sudo journalctl -u cloudflare-ddns -f
```

1. Otros comandos útiles:

```bash
# Detener el servicio
sudo systemctl stop cloudflare-ddns

# Reiniciar el servicio
sudo systemctl restart cloudflare-ddns

# Deshabilitar el servicio
sudo systemctl disable cloudflare-ddns

# Ver logs de las últimas 100 líneas
sudo journalctl -u cloudflare-ddns -n 100
```

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

⭐ Si este proyecto te ha sido útil, considera darle una estrella en GitHub
