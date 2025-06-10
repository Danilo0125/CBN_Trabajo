/**
 * Dashboard de sensores en tiempo real
 * 
 * Este archivo contiene toda la lógica del dashboard para monitoreo
 * de sensores industriales en tiempo real.
 */

// Configuración de Socket.IO con mejor manejo de errores
const socket = io({
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    timeout: 5000
});

// Variables para almacenar datos
let tempData = [];
let vibrationData = [];
let pressureData = [];
let timeLabels = [];
const maxDataPoints = 100; // Máximo de puntos a mostrar en los gráficos

// Estado de la máquina - Cambiado a true por defecto
let maquinaEncendida = true;

// Elementos DOM
const statusIndicator = document.getElementById('status-indicator');
const connectionStatus = document.getElementById('connection-status');
const tempValue = document.getElementById('temp-value');
const vibrationValue = document.getElementById('vibration-value');
const pressureValue = document.getElementById('pressure-value');
const powerButton = document.getElementById('power-button');
const powerText = document.getElementById('power-text');

/**
 * Carga los datos iniciales desde el servidor
 */
async function cargarDatosIniciales() {
    try {
        console.log("Cargando datos iniciales...");
        const response = await fetch('/api/datos');
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const datos = await response.json();
        
        if (datos && datos.length > 0) {
            console.log(`Cargados ${datos.length} datos iniciales`);
            // Cargar los últimos 50 datos
            const datosIniciales = datos.slice(-50);
            
            datosIniciales.forEach(data => {
                const time = new Date(data.timestamp).toLocaleTimeString();
                timeLabels.push(time);
                tempData.push(data.temperatura);
                vibrationData.push(data.vibracion);
                pressureData.push(data.presion);
            });
            
            // Actualizar valores actuales con el último dato
            const ultimoDato = datosIniciales[datosIniciales.length - 1];
            tempValue.textContent = `${ultimoDato.temperatura}°C`;
            vibrationValue.textContent = `${ultimoDato.vibracion} mm/s`;
            pressureValue.textContent = `${ultimoDato.presion} bar`;
            
            // Actualizar gráficos
            tempChart.update();
            vibrationChart.update();
            pressureChart.update();
        } else {
            console.log("No hay datos iniciales disponibles");
        }
    } catch (error) {
        console.error('Error cargando datos iniciales:', error);
        // Mostrar mensaje en la interfaz
        const connectionStatus = document.getElementById('connection-status');
        if (connectionStatus) {
            connectionStatus.textContent = 'Error cargando datos';
            connectionStatus.classList.add('text-red-500');
        }
    }
}

/**
 * Actualiza el estado visual del botón de encendido/apagado
 */
function actualizarBotonEncendido(encendido) {
    if (encendido) {
        powerButton.classList.remove('bg-green-500', 'hover:bg-green-600');
        powerButton.classList.add('bg-red-500', 'hover:bg-red-600');
        powerText.textContent = 'Apagar Máquina';
    } else {
        powerButton.classList.remove('bg-red-500', 'hover:bg-red-600');
        powerButton.classList.add('bg-green-500', 'hover:bg-green-600');
        powerText.textContent = 'Encender Máquina';
    }
    maquinaEncendida = encendido;
}

/**
 * Cambia el estado de la máquina (encendido/apagado)
 */
function toggleMaquina() {
    // Si el botón está deshabilitado, no hacer nada
    if (powerButton.disabled) {
        mostrarNotificacion('No se puede cambiar el estado: sensor inactivo', 'error');
        return;
    }
    
    // Deshabilitar el botón temporalmente para evitar clics múltiples
    powerButton.disabled = true;
    
    // Indicar visualmente que se está procesando
    const originalText = powerText.textContent;
    powerText.textContent = maquinaEncendida ? 'Apagando...' : 'Encendiendo...';
    
    // Enviar comando al servidor
    socket.emit('cambiar_estado_maquina', { encender: !maquinaEncendida }, (response) => {
        // Callback cuando el servidor responde (opcional)
        if (response && response.success) {
            console.log(`Máquina ${response.estado} correctamente`);
        } else {
            // Si hay error, revertir el estado del botón
            console.error('Error al cambiar el estado de la máquina');
            powerText.textContent = originalText;
        }
        
        // Re-habilitar el botón después de procesar
        setTimeout(() => powerButton.disabled = false, 500);
    });
    
    // El estado real se actualizará cuando el servidor envíe el evento 'estado_maquina'
    // No actualizamos aquí para evitar inconsistencias
}

// Configuración de gráficos
const chartConfig = {
    type: 'line',
    options: {
        responsive: true,
        scales: {
            x: {
                display: false
            }
        },
        plugins: {
            legend: {
                display: false
            }
        },
        animation: {
            duration: 0
        }
    }
};

// Crear gráficos
const tempChart = new Chart(document.getElementById('tempChart'), {
    ...chartConfig,
    data: {
        labels: timeLabels,
        datasets: [{
            data: tempData,
            borderColor: 'rgb(239, 68, 68)',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            fill: true
        }]
    }
});

const vibrationChart = new Chart(document.getElementById('vibrationChart'), {
    ...chartConfig,
    data: {
        labels: timeLabels,
        datasets: [{
            data: vibrationData,
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true
        }]
    }
});

const pressureChart = new Chart(document.getElementById('pressureChart'), {
    ...chartConfig,
    data: {
        labels: timeLabels,
        datasets: [{
            data: pressureData,
            borderColor: 'rgb(34, 197, 94)',
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            fill: true
        }]
    }
});

/**
 * Umbrales de alerta para los sensores
 */
const LIMITES = {
    temperatura: {
        advertencia: 70,
        critico: 85
    },
    vibracion: {
        advertencia: 7,
        critico: 9
    },
    presion: {
        advertencia: 150,
        critico: 200
    }
};

/**
 * Estado de las alertas activas
 */
let alertaActiva = false;
let tipoAlerta = null;

/**
 * Verifica si hay valores fuera de rango y muestra alertas
 */
function verificarAlertas(data) {
    // Verificar temperatura
    if (data.temperatura >= LIMITES.temperatura.critico) {
        mostrarAlerta('critico', 'temperatura', data.temperatura);
    } else if (data.temperatura >= LIMITES.temperatura.advertencia) {
        mostrarAlerta('advertencia', 'temperatura', data.temperatura);
    }
    
    // Verificar vibración
    else if (data.vibracion >= LIMITES.vibracion.critico) {
        mostrarAlerta('critico', 'vibracion', data.vibracion);
    } else if (data.vibracion >= LIMITES.vibracion.advertencia) {
        mostrarAlerta('advertencia', 'vibracion', data.vibracion);
    }
    
    // Verificar presión
    else if (data.presion >= LIMITES.presion.critico) {
        mostrarAlerta('critico', 'presion', data.presion);
    } else if (data.presion >= LIMITES.presion.advertencia) {
        mostrarAlerta('advertencia', 'presion', data.presion);
    }
    
    // Si no hay ninguna alerta pero había una activa, ocultar
    else if (alertaActiva) {
        ocultarAlerta();
    }
}

/**
 * Muestra una alerta en la interfaz
 */
function mostrarAlerta(nivel, sensor, valor) {
    // Si ya hay una alerta del mismo tipo, no hacer nada
    if (alertaActiva && tipoAlerta === `${nivel}-${sensor}`) {
        return;
    }
    
    // Actualizar estado de alerta
    alertaActiva = true;
    tipoAlerta = `${nivel}-${sensor}`;
    
    // Crear elemento de alerta si no existe
    let alertaContainer = document.getElementById('alerta-container');
    if (!alertaContainer) {
        alertaContainer = document.createElement('div');
        alertaContainer.id = 'alerta-container';
        alertaContainer.className = 'fixed top-4 right-4 z-50 w-80 shadow-lg rounded-lg overflow-hidden';
        document.body.appendChild(alertaContainer);
    }
    
    // Definir colores y mensaje según nivel
    const colores = nivel === 'critico' ? 'bg-red-600 border-red-800' : 'bg-yellow-500 border-yellow-700';
    const titulo = nivel === 'critico' ? '¡ALERTA CRÍTICA!' : 'Advertencia';
    
    // Mapear sensor a nombre legible
    const sensorNombre = {
        'temperatura': 'Temperatura',
        'vibracion': 'Vibración',
        'presion': 'Presión'
    }[sensor];
    
    // Mapear sensor a unidad
    const unidad = {
        'temperatura': '°C',
        'vibracion': 'mm/s',
        'presion': 'bar'
    }[sensor];
    
    // Construir mensaje
    const mensaje = `${sensorNombre} elevada: <strong>${valor} ${unidad}</strong>`;
    const accion = nivel === 'critico' 
        ? 'Se recomienda apagar la máquina inmediatamente para prevenir daños.'
        : 'Monitoree la situación y considere reducir la carga de trabajo.';
    
    // Crear HTML de la alerta
    alertaContainer.innerHTML = `
        <div class="${colores} border-l-4 p-4">
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <svg class="h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                </div>
                <div class="ml-3 w-full">
                    <h3 class="text-white font-bold">${titulo}</h3>
                    <div class="mt-1 text-white text-sm">${mensaje}</div>
                    <div class="mt-2 text-white text-xs">${accion}</div>
                    <div class="mt-3 flex justify-between">
                        <button id="btn-apagar-emergencia" class="px-3 py-1 bg-white text-red-600 hover:bg-red-100 rounded-md text-sm font-medium">
                            Apagar Máquina
                        </button>
                        <button id="btn-cerrar-alerta" class="px-3 py-1 bg-transparent border border-white text-white hover:bg-white hover:text-red-600 rounded-md text-sm">
                            Cerrar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Agregar event listeners a los botones
    document.getElementById('btn-apagar-emergencia').addEventListener('click', () => {
        // Apagar la máquina
        if (maquinaEncendida) {
            toggleMaquina();
        }
        // Cerrar la alerta
        ocultarAlerta();
    });
    
    document.getElementById('btn-cerrar-alerta').addEventListener('click', ocultarAlerta);
    
    // Reproducir sonido de alerta si es crítica
    if (nivel === 'critico') {
        reproducirSonidoAlerta();
    }
}

/**
 * Oculta la alerta activa
 */
function ocultarAlerta() {
    const alertaContainer = document.getElementById('alerta-container');
    if (alertaContainer) {
        alertaContainer.remove();
    }
    alertaActiva = false;
    tipoAlerta = null;
}

/**
 * Reproduce un sonido de alerta
 */
function reproducirSonidoAlerta() {
    // Crear un oscilador simple para el sonido de alarma
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();
        
        oscillator.type = 'square';
        oscillator.frequency.setValueAtTime(440, audioCtx.currentTime); // Nota A4
        
        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
        
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        
        oscillator.start();
        setTimeout(() => {
            oscillator.stop();
        }, 500);
    } catch (e) {
        console.log('Audio no soportado o bloqueado');
    }
}

// Eventos de Socket.IO
socket.on('connect', () => {
    statusIndicator.className = 'w-3 h-3 bg-green-500 rounded-full mr-2';
    connectionStatus.textContent = 'Conectado';
    
    // Cargar datos iniciales cuando se conecta
    cargarDatosIniciales();
});

socket.on('disconnect', () => {
    statusIndicator.className = 'w-3 h-3 bg-red-500 rounded-full mr-2';
    connectionStatus.textContent = 'Desconectado';
});

// Nuevo evento para manejar actualizaciones de estado de sensores
socket.on('estado_sensores', (data) => {
    if (!data.activos) {
        statusIndicator.className = 'w-3 h-3 bg-yellow-500 rounded-full mr-2';
        connectionStatus.textContent = 'Sensor inactivo';
        connectionStatus.classList.add('text-yellow-500');
        connectionStatus.classList.remove('text-green-500', 'text-red-500');
        
        // Cambiar color de los valores para indicar valores cero
        tempValue.classList.add('text-gray-400');
        vibrationValue.classList.add('text-gray-400');
        pressureValue.classList.add('text-gray-400');
        
        // Deshabilitar el botón de encendido/apagado cuando no hay sensor activo
        powerButton.disabled = true;
        powerButton.classList.add('opacity-50', 'cursor-not-allowed');
        
        // Mostrar notificación al usuario
        mostrarNotificacion('Sensor desconectado - esperando reconexión', 'warning');
    } else {
        statusIndicator.className = 'w-3 h-3 bg-green-500 rounded-full mr-2';
        connectionStatus.textContent = 'Sensor activo';
        connectionStatus.classList.add('text-green-500');
        connectionStatus.classList.remove('text-yellow-500', 'text-red-500');
        
        // Restaurar colores normales
        tempValue.classList.remove('text-gray-400');
        vibrationValue.classList.remove('text-gray-400');
        pressureValue.classList.remove('text-gray-400');
        
        // Habilitar el botón de encendido/apagado cuando hay sensor activo
        powerButton.disabled = false;
        powerButton.classList.remove('opacity-50', 'cursor-not-allowed');
        
        // Mostrar notificación al usuario
        mostrarNotificacion('Sensor conectado', 'success');
    }
});

// Evento para cambios en el estado de la máquina
socket.on('estado_maquina', (data) => {
    actualizarBotonEncendido(data.encendida);
    
    // Mostrar mensaje de cambio de estado
    const mensaje = data.encendida ? 'Máquina encendida' : 'Máquina apagada';
    console.log(mensaje);
    
    // Mostrar notificación al usuario
    mostrarNotificacion(mensaje, data.encendida ? 'success' : 'info');
});

/**
 * Muestra una notificación temporal al usuario
 */
function mostrarNotificacion(mensaje, tipo = 'info') {
    // Crear elemento de notificación si no existe
    let notifContainer = document.getElementById('notif-container');
    if (!notifContainer) {
        notifContainer = document.createElement('div');
        notifContainer.id = 'notif-container';
        notifContainer.className = 'fixed bottom-4 right-4 z-50';
        document.body.appendChild(notifContainer);
    }
    
    // Crear notificación
    const notifId = 'notif-' + Date.now();
    const notif = document.createElement('div');
    notif.id = notifId;
    
    // Estilos según el tipo
    let bgColor = 'bg-blue-500';
    if (tipo === 'success') bgColor = 'bg-green-500';
    if (tipo === 'error') bgColor = 'bg-red-500';
    if (tipo === 'warning') bgColor = 'bg-yellow-500';
    
    notif.className = `${bgColor} text-white rounded-lg shadow-lg p-4 mb-3 transform transition-all duration-300 ease-in-out`;
    notif.innerHTML = mensaje;
    
    // Añadir al contenedor
    notifContainer.appendChild(notif);
    
    // Eliminar después de 3 segundos
    setTimeout(() => {
        notif.classList.add('opacity-0', 'translate-x-full');
        setTimeout(() => notif.remove(), 300);
    }, 3000);
}

// Evento para nuevos datos de sensores
socket.on('nuevos_datos', (data) => {
    // Limitar actualizaciones de UI para evitar sobrecarga del navegador
    // Solo actualizar los valores numéricos en cada dato recibido
    tempValue.textContent = `${data.temperatura}°C`;
    vibrationValue.textContent = `${data.vibracion} mm/s`;
    pressureValue.textContent = `${data.presion} bar`;

    // Verificar si hay valores que requieren alertas
    verificarAlertas(data);

    // Agregar datos a los arrays para los gráficos
    const time = new Date(data.timestamp).toLocaleTimeString();
    timeLabels.push(time);
    tempData.push(data.temperatura);
    vibrationData.push(data.vibracion);
    pressureData.push(data.presion);

    // Mantener solo los últimos N puntos
    if (timeLabels.length > maxDataPoints) {
        timeLabels.shift();
        tempData.shift();
        vibrationData.shift();
        pressureData.shift();
    }

    // Actualizar gráficos con una frecuencia más baja para mejor rendimiento
    // Actualizar cada ~250ms (4 veces por segundo) en lugar de cada mensaje
    if (!window.lastChartUpdate || Date.now() - window.lastChartUpdate > 250) {
        tempChart.update('none');
        vibrationChart.update('none');
        pressureChart.update('none');
        window.lastChartUpdate = Date.now();
    }
});

// Evento del botón de encendido/apagado
powerButton.addEventListener('click', toggleMaquina);

// Evento DOMContentLoaded - Actualizar estado del botón inmediatamente
document.addEventListener('DOMContentLoaded', () => {
    // Actualizar el botón inmediatamente para mostrar "Apagar Máquina"
    actualizarBotonEncendido(maquinaEncendida);
    
    // Cargar datos iniciales
    setTimeout(cargarDatosIniciales, 1000);
});

// Mejorar manejo de errores de conexión
socket.on('connect_error', (error) => {
    console.error('Error de conexión:', error);
    statusIndicator.className = 'w-3 h-3 bg-red-500 rounded-full mr-2';
    connectionStatus.textContent = 'Error de conexión';
    connectionStatus.classList.add('text-red-500');
    connectionStatus.classList.remove('text-green-500', 'text-yellow-500');
    
    // Mostrar notificación visible al usuario
    mostrarNotificacion('Error de conexión con el servidor', 'error');
    
    // Intentar reconectar automáticamente después de 3 segundos
    setTimeout(() => {
        if (!socket.connected) {
            reintentarConexion();
        }
    }, 3000);
});

// Agregar función para reintentar la conexión manualmente
function reintentarConexion() {
    statusIndicator.className = 'w-3 h-3 bg-yellow-500 rounded-full mr-2';
    connectionStatus.textContent = 'Reconectando...';
    socket.connect();
}
