# Sistema de Monitoreo de Sensores en Tiempo Real

Este proyecto implementa un sistema de monitoreo de sensores industriales en tiempo real, con un servidor web que muestra los datos a través de una interfaz gráfica.

## Estructura del Proyecto

- `servidor/` - Contiene el servidor Flask y la interfaz web
- `cliente/` - Contiene el simulador de sensores

## Requisitos

- Python 3.7 o superior
- Paquetes requeridos: flask, flask-socketio, python-socketio, numpy, pandas

## Instalación

Instala las dependencias necesarias:

```bash
pip install flask flask-socketio python-socketio numpy pandas matplotlib
```

## Uso

1. **Inicia el servidor Flask**:

```bash
cd servidor
python flask_server.py
```

El servidor estará disponible en: http://localhost:5000

2. **Inicia el simulador de sensores**:

```bash
cd cliente
python sensor_simulado.py
```

3. **Accede al Dashboard**:
   - Abre un navegador web y ve a http://localhost:5000
   - Verás el dashboard con los datos de los sensores en tiempo real

## Funcionalidades

- **Dashboard web** con gráficos en tiempo real
- **Control de la máquina** (encendido/apagado)
- **Alertas** para valores anormales
- **Simulación de fallos** aleatorios para pruebas

## Solución de Problemas

Si encuentras problemas de conexión:

1. Verifica que el servidor esté en ejecución antes de iniciar el simulador
2. Comprueba que no haya otro proceso usando el puerto 5000
3. Revisa la configuración en `config.py` si necesitas cambiar el host o puerto

## Licencia

Este proyecto es para fines educativos.
