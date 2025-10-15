# Documentos Legales - Sistema de Parqueaderos

## 📄 Descripción

Este directorio contiene los documentos legales del Sistema de Parqueaderos:
- **Política de Privacidad**: Cómo se recopila, usa y protege la información personal
- **Términos de Servicio**: Reglas, obligaciones y limitaciones del uso del sistema

## 🌐 Acceso

Los documentos legales están disponibles públicamente a través de los siguientes endpoints:

### Desarrollo Local
```
http://localhost:8000/privacy-policy
http://localhost:8000/terms-of-service
```

### A través de Kong (Load Balancer)
```
http://localhost:8000/privacy-policy
http://localhost:8000/terms-of-service
```

### Producción (Ngrok)
```
https://geometric-mawkish-leeanna.ngrok-free.dev/privacy-policy
https://geometric-mawkish-leeanna.ngrok-free.dev/terms-of-service
```

## 📋 Contenido

### Política de Privacidad

La política de privacidad cubre:

1. **Información que Recopilamos**
   - Datos de identificación (número de WhatsApp, nombre)
   - Información de uso (historial de conversaciones, consultas)
   - Información de ubicación (para gestores)

2. **Cómo Utilizamos su Información**
   - Prestación del servicio
   - Envío de notificaciones
   - Gestión de parqueaderos
   - Mejora del servicio

3. **Seguridad de los Datos**
   - Cifrado
   - Controles de acceso
   - Monitoreo continuo

4. **Derechos del Usuario**
   - Acceso a información
   - Rectificación
   - Eliminación
   - Portabilidad
   - Oposición

5. **Cumplimiento Legal**
   - Ley 1581 de 2012 (Colombia)
   - Decreto 1377 de 2013

### Términos de Servicio

Los términos de servicio incluyen:

1. **Aceptación de Términos**
   - Reconocimiento y aceptación obligatoria
   - Efectos del uso continuado

2. **Descripción del Servicio**
   - Funcionalidades para conductores
   - Herramientas para gestores
   - Limitaciones del servicio informativo

3. **Requisitos de Uso**
   - Elegibilidad (18+ años)
   - Cuenta de WhatsApp activa
   - Responsabilidad de información

4. **Conducta del Usuario**
   - Uso apropiado
   - Conductas prohibidas
   - Consecuencias de violaciones

5. **Responsabilidades y Limitaciones**
   - Descargo de garantías
   - Limitación de responsabilidad
   - Exclusiones

6. **Propiedad Intelectual**
   - Derechos de propiedad
   - Licencias de uso

7. **Terminación del Servicio**
   - Por el usuario
   - Por el sistema
   - Efectos de la terminación

8. **Disposiciones Legales**
   - Ley aplicable (Colombia)
   - Jurisdicción
   - Resolución de disputas

9. **Indemnización**
   - Obligaciones del usuario
   - Protección del sistema

10. **Modificaciones**
    - Cambios al servicio
    - Actualizaciones de términos

## 🔧 Implementación Técnica

### Estructura de Archivos

```
app/
├── static/
│   └── privacy-policy.html    # Archivo HTML de la política
└── main.py                     # Endpoint FastAPI
```

### Endpoint

```python
@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy():
    """
    Retorna la política de privacidad del sistema
    """
    # Lee y retorna el archivo HTML
```

## 🎨 Características del HTML

- **Responsive Design**: Se adapta a dispositivos móviles y desktop
- **Estilo Profesional**: Diseño limpio y fácil de leer
- **Secciones Claras**: Organizado en secciones numeradas
- **Información de Contacto**: Incluye formas de contactar al equipo
- **Última Actualización**: Muestra la fecha de la última modificación

## 📝 Actualización de Contenido

Para actualizar la política de privacidad:

1. Edita el archivo `app/static/privacy-policy.html`
2. Actualiza la fecha en la sección "Última actualización"
3. Guarda los cambios
4. Reinicia el servicio (el cambio es automático con hot-reload en desarrollo)

```bash
# En desarrollo (con hot-reload activo)
# Los cambios se aplican automáticamente

# En producción
docker-compose restart fastapi-1 fastapi-2 fastapi-3
```

## 🔗 Integración con WhatsApp

Puedes compartir la política de privacidad en mensajes de WhatsApp:

```python
# Ejemplo de cómo incluir el link en un mensaje
mensaje = f"""
Bienvenido al Sistema de Parqueaderos.

Para usar nuestro servicio, debes aceptar nuestra política de privacidad.

📄 Lee nuestra política aquí:
{NGROK_DOMAIN}/privacy-policy

¿Aceptas los términos? (sí/no)
"""
```

## 🧪 Testing

### Probar en Local

```bash
# Iniciar el servidor
docker-compose up

# En otro terminal, probar el endpoint
curl http://localhost:8000/privacy-policy

# O abrir en navegador
open http://localhost:8000/privacy-policy
```

### Verificar a través de Kong

```bash
# Kong distribuye la petición entre las instancias
curl http://localhost:8000/privacy-policy
```

## 📊 Monitoreo

Kong registra todas las peticiones a este endpoint. Para ver las métricas:

```bash
# Ver métricas de Prometheus
curl http://localhost:8001/metrics | grep privacy

# Ver logs de Kong
docker-compose logs -f kong
```

## 🔒 Seguridad

### HTTPS

En producción, la política de privacidad se sirve sobre HTTPS a través de Ngrok:

```
https://your-domain.ngrok-free.app/privacy-policy
```

### Rate Limiting

Kong aplica rate limiting automáticamente (configurado en 1000 req/min).

### CORS

El endpoint tiene CORS habilitado para permitir acceso desde diferentes dominios.

## 📱 Uso en la Aplicación

### Flujo de Registro

1. Usuario inicia conversación con el bot
2. Bot envía mensaje de bienvenida con link a política de privacidad
3. Usuario lee la política
4. Usuario acepta o rechaza
5. Si acepta, se completa el registro
6. Si rechaza, se cancela el proceso

### Ejemplo de Implementación

```python
def enviar_solicitud_aceptacion_privacidad(user_id: str):
    """Envía mensaje solicitando aceptación de política de privacidad"""
    mensaje = f"""
🔒 *Política de Privacidad*

Antes de continuar, necesitas aceptar nuestra política de privacidad.

📄 Puedes leerla aquí:
{os.getenv('NGROK_DOMAIN')}/privacy-policy

La política describe:
✓ Qué información recopilamos
✓ Cómo la usamos
✓ Cómo la protegemos
✓ Tus derechos

¿Aceptas los términos?
    """
    
    # Enviar mensaje con botones interactivos
    send_buttons(
        user_id,
        mensaje,
        [
            {"id": "aceptar_privacidad", "title": "✅ Aceptar"},
            {"id": "rechazar_privacidad", "title": "❌ Rechazar"},
            {"id": "leer_mas", "title": "📖 Leer política"}
        ]
    )
```

## 🌍 Cumplimiento Legal

### Colombia

Este documento cumple con:
- Ley 1581 de 2012 (Habeas Data)
- Decreto 1377 de 2013
- Circular Externa 002 de 2015 de la SIC

### Internacional

También considera principios de:
- GDPR (Unión Europea)
- CCPA (California)
- Mejores prácticas internacionales

## 📞 Soporte

Para preguntas sobre la política de privacidad:

- **WhatsApp**: Envía un mensaje al bot
- **Email**: privacy@parqueaderos.com
- **GitHub Issues**: Para reportar problemas técnicos

## 🔄 Historial de Cambios

| Fecha | Versión | Cambios |
|-------|---------|---------|
| 2025-10-13 | 1.0.0 | Versión inicial |

## 📚 Referencias

- [Ley 1581 de 2012](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981)
- [Decreto 1377 de 2013](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=53646)
- [Superintendencia de Industria y Comercio](https://www.sic.gov.co/)
