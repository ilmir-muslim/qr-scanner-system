<template>
    <div class="scan-container">
        <div class="scan-header">
            <h1>Сканирование QR кодов</h1>
            <div class="mode-selector">
                <button @click="scanMode = 'camera'" :class="{ active: scanMode === 'camera' }">
                    Камера
                </button>
                <button @click="scanMode = 'scanner'" :class="{ active: scanMode === 'scanner' }">
                    Сканер
                </button>
                <button @click="scanMode = 'manual'" :class="{ active: scanMode === 'manual' }">
                    Вручную
                </button>
            </div>
        </div>

        <div class="scan-content">
            <!-- Режим камеры -->
            <div v-if="scanMode === 'camera'" class="camera-mode">
                <div class="camera-container">
                    <video ref="videoElement" v-show="!capturedImage" autoplay playsinline></video>
                    <canvas ref="canvasElement" style="display: none;"></canvas>

                    <div v-if="capturedImage" class="captured-image">
                        <img :src="capturedImage" alt="Captured QR">
                        <div class="capture-actions">
                            <button @click="retakePhoto">Переснять</button>
                            <button @click="processQRCode" :disabled="processing">
                                {{ processing ? 'Обработка...' : 'Сканировать QR' }}
                            </button>
                        </div>
                    </div>

                    <div v-else class="camera-controls">
                        <button @click="startCamera" :disabled="cameraActive">
                            {{ cameraActive ? 'Камера активна' : 'Включить камеру' }}
                        </button>
                        <button @click="capturePhoto" :disabled="!cameraActive">
                            Сделать фото
                        </button>
                        <button @click="switchCamera" v-if="cameras.length > 1">
                            Переключить камеру
                        </button>
                    </div>
                </div>
            </div>

            <!-- Режим сканера -->
            <div v-else-if="scanMode === 'scanner'" class="scanner-mode">
                <div class="scanner-input">
                    <input type="text" v-model="scannerInput" placeholder="Наведите сканер на QR код..."
                        ref="scannerInput" @keyup.enter="processScannerInput" />
                    <button @click="processScannerInput" :disabled="!scannerInput">
                        Обработать
                    </button>
                </div>

                <div class="scanner-status">
                    <p v-if="scannerConnected">Сканер подключен</p>
                    <p v-else style="color: #f44336;">Сканер не обнаружен</p>
                </div>
            </div>

            <!-- Ручной режим -->
            <div v-else class="manual-mode">
                <div class="manual-input">
                    <textarea v-model="manualInput" placeholder="Введите данные QR кода вручную..." rows="4"></textarea>
                    <button @click="processManualInput" :disabled="!manualInput">
                        Сохранить и распечатать
                    </button>
                </div>
            </div>

            <!-- Настройки принтера -->
            <div class="printer-settings">
                <h3>Настройки печати</h3>
                <div class="printer-select">
                    <select v-model="selectedPrinter">
                        <option value="default">Принтер по умолчанию</option>
                        <option value="label">Принтер этикеток</option>
                    </select>
                    <button @click="registerAsPrinter" :class="{ active: isPrinterClient }">
                        {{ isPrinterClient ? '✓ Этот клиент для печати' : 'Использовать для печати' }}
                    </button>
                </div>

                <div class="print-preview" v-if="lastQRCode">
                    <h4>Предпросмотр:</h4>
                    <img :src="lastQRCode" alt="QR Code Preview" />
                    <p>{{ lastQRData }}</p>
                </div>
            </div>

            <!-- История последних сканов -->
            <div class="recent-scans">
                <h3>Последние сканирования</h3>
                <ul>
                    <li v-for="scan in recentScans" :key="scan.id">
                        <span class="scan-time">{{ formatTime(scan.scanned_at) }}</span>
                        <span class="scan-data">{{ scan.qr_data }}</span>
                        <span class="scan-status" :class="{ printed: scan.printed }">
                            {{ scan.printed ? '✓' : '○' }}
                        </span>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useToast } from '../services/toast'
import api from '../services/api'
import printService from '../services/print'
import scannerService from '../services/scanner'

export default {
    name: 'ScanView',
    setup() {
        const videoElement = ref(null)
        const canvasElement = ref(null)
        const scannerInput = ref(null)

        const scanMode = ref('camera')
        const cameraActive = ref(false)
        const capturedImage = ref(null)
        const processing = ref(false)
        const scannerConnected = ref(false)
        const scannerInputValue = ref('')
        const manualInput = ref('')
        const selectedPrinter = ref('default')
        const isPrinterClient = ref(false)
        const lastQRCode = ref(null)
        const lastQRData = ref('')
        const recentScans = ref([])
        const cameras = ref([])
        const currentCamera = ref(0)

        let stream = null
        let wsConnection = null
        const clientId = generateClientId()

        // Генерация ID клиента
        function generateClientId() {
            return 'client_' + Math.random().toString(36).substr(2, 9)
        }

        // Инициализация
        onMounted(async () => {
            // Проверяем сканер
            checkScanner()

            // Загружаем историю
            loadRecentScans()

            // Подключаемся к WebSocket
            connectWebSocket()

            // Фокус на поле сканера
            if (scannerInput.value) {
                scannerInput.value.focus()
            }
        })

        onUnmounted(() => {
            stopCamera()
            if (wsConnection) {
                wsConnection.close()
            }
        })

        // Работа с камерой
        async function startCamera() {
            try {
                const constraints = {
                    video: {
                        facingMode: 'environment',
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    }
                }

                stream = await navigator.mediaDevices.getUserMedia(constraints)

                if (videoElement.value) {
                    videoElement.value.srcObject = stream
                    cameraActive.value = true
                }

                // Получаем список камер
                const devices = await navigator.mediaDevices.enumerateDevices()
                cameras.value = devices.filter(device => device.kind === 'videoinput')

            } catch (error) {
                console.error('Ошибка доступа к камере:', error)
                useToast().error('Не удалось получить доступ к камере')
            }
        }

        function stopCamera() {
            if (stream) {
                stream.getTracks().forEach(track => track.stop())
                stream = null
                cameraActive.value = false
            }
        }

        function switchCamera() {
            if (cameras.value.length > 1) {
                currentCamera.value = (currentCamera.value + 1) % cameras.value.length
                stopCamera()
                startCamera()
            }
        }

        function capturePhoto() {
            if (!videoElement.value || !canvasElement.value) return

            const video = videoElement.value
            const canvas = canvasElement.value

            canvas.width = video.videoWidth
            canvas.height = video.videoHeight

            const context = canvas.getContext('2d')
            context.drawImage(video, 0, 0, canvas.width, canvas.height)

            capturedImage.value = canvas.toDataURL('image/jpeg')
        }

        function retakePhoto() {
            capturedImage.value = null
        }

        // Обработка QR кода с фото
        async function processQRCode() {
            if (!capturedImage.value) return

            processing.value = true

            try {
                const response = await api.scanFromImage(capturedImage.value, clientId)

                lastQRData.value = response.qr_data
                lastQRCode.value = await api.generateQRCode(response.qr_data)

                useToast().success('QR код успешно распознан и отправлен на печать')

                // Добавляем в историю
                recentScans.value.unshift(response)
                if (recentScans.value.length > 10) {
                    recentScans.value.pop()
                }

                // Сбрасываем фото через 2 секунды
                setTimeout(() => {
                    capturedImage.value = null
                }, 2000)

            } catch (error) {
                useToast().error('Ошибка при распознавании QR кода')
                console.error(error)
            } finally {
                processing.value = false
            }
        }

        // Проверка сканера
        function checkScanner() {
            // Эмуляция проверки подключения сканера
            scannerConnected.value = true
        }

        // Обработка ввода со сканера
        function processScannerInput() {
            if (!scannerInputValue.value.trim()) return

            api.manualScan(scannerInputValue.value, 'scanner')
                .then(response => {
                    useToast().success('Данные сканера сохранены')
                    scannerInputValue.value = ''
                    loadRecentScans()

                    if (scannerInput.value) {
                        scannerInput.value.focus()
                    }
                })
                .catch(error => {
                    useToast().error('Ошибка при сохранении данных сканера')
                    console.error(error)
                })
        }

        // Ручной ввод
        function processManualInput() {
            if (!manualInput.value.trim()) return

            api.createScan({
                qr_data: manualInput.value,
                scan_type: 'manual',
                printer_id: selectedPrinter.value
            })
                .then(response => {
                    useToast().success('Данные сохранены')
                    manualInput.value = ''
                    loadRecentScans()
                })
                .catch(error => {
                    useToast().error('Ошибка при сохранении данных')
                    console.error(error)
                })
        }

        // WebSocket подключение
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
            const wsUrl = `${protocol}//${window.location.host}/api/v1/printers/ws/print/${clientId}`

            wsConnection = new WebSocket(wsUrl)

            wsConnection.onopen = () => {
                console.log('WebSocket connected')

                // Регистрируем как клиент печати
                wsConnection.send(JSON.stringify({
                    type: 'register_printer',
                    printer_name: 'Web Client Printer'
                }))
            }

            wsConnection.onmessage = (event) => {
                const data = JSON.parse(event.data)

                if (data.type === 'print') {
                    // Обработка команды печати
                    handlePrintCommand(data)
                }
            }

            wsConnection.onerror = (error) => {
                console.error('WebSocket error:', error)
            }

            wsConnection.onclose = () => {
                console.log('WebSocket disconnected')
                // Пытаемся переподключиться через 5 секунд
                setTimeout(connectWebSocket, 5000)
            }
        }

        // Обработка команды печати
        function handlePrintCommand(data) {
            if (!isPrinterClient.value) return

            useToast().info('Получена команда на печать')

            // Печатаем QR код
            printService.printQRCode(data.qr_image, data.qr_data)
                .then(() => {
                    useToast().success('Печать завершена')
                })
                .catch(error => {
                    useToast().error('Ошибка при печати')
                    console.error(error)
                })
        }

        // Регистрация как клиент печати
        function registerAsPrinter() {
            isPrinterClient.value = !isPrinterClient.value

            if (isPrinterClient.value && wsConnection) {
                wsConnection.send(JSON.stringify({
                    type: 'set_default'
                }))
                useToast().success('Этот клиент установлен для печати')
            }
        }

        // Загрузка истории
        function loadRecentScans() {
            api.getScans(0, 5)
                .then(response => {
                    recentScans.value = response
                })
                .catch(error => {
                    console.error('Ошибка загрузки истории:', error)
                })
        }

        // Форматирование времени
        function formatTime(dateString) {
            const date = new Date(dateString)
            return date.toLocaleTimeString()
        }

        return {
            // Refs
            videoElement,
            canvasElement,
            scannerInput,
            scanMode,
            cameraActive,
            capturedImage,
            processing,
            scannerConnected,
            scannerInput: scannerInputValue,
            manualInput,
            selectedPrinter,
            isPrinterClient,
            lastQRCode,
            lastQRData,
            recentScans,
            cameras,
            currentCamera,

            // Methods
            startCamera,
            stopCamera,
            switchCamera,
            capturePhoto,
            retakePhoto,
            processQRCode,
            processScannerInput,
            processManualInput,
            registerAsPrinter,
            formatTime
        }
    }
}
</script>

<style scoped>
.scan-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.scan-header {
    margin-bottom: 30px;
}

.mode-selector {
    display: flex;
    gap: 10px;
    margin-top: 15px;
}

.mode-selector button {
    padding: 10px 20px;
    border: 2px solid #ddd;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
}

.mode-selector button.active {
    background: #2196F3;
    color: white;
    border-color: #2196F3;
}

.camera-container {
    background: #000;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 20px;
}

video {
    width: 100%;
    max-height: 500px;
    object-fit: contain;
}

.captured-image {
    text-align: center;
    padding: 20px;
}

.captured-image img {
    max-width: 100%;
    max-height: 400px;
    border: 2px solid white;
    border-radius: 4px;
}

.capture-actions {
    margin-top: 20px;
    display: flex;
    gap: 10px;
    justify-content: center;
}

.camera-controls {
    padding: 20px;
    display: flex;
    gap: 10px;
    justify-content: center;
    background: #333;
}

.scanner-input {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.scanner-input input {
    flex: 1;
    padding: 15px;
    font-size: 18px;
    border: 2px solid #2196F3;
    border-radius: 4px;
}

.manual-input {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.manual-input textarea {
    padding: 15px;
    font-size: 16px;
    border: 2px solid #4CAF50;
    border-radius: 4px;
    resize: vertical;
}

.printer-settings {
    background: #f5f5f5;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
}

.printer-select {
    display: flex;
    gap: 10px;
    margin: 15px 0;
}

.printer-select select {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    flex: 1;
}

.printer-select button.active {
    background: #4CAF50;
    color: white;
}

.print-preview {
    margin-top: 20px;
    text-align: center;
}

.print-preview img {
    width: 200px;
    height: 200px;
    margin: 10px 0;
}

.recent-scans {
    margin-top: 30px;
}

.recent-scans ul {
    list-style: none;
    padding: 0;
}

.recent-scans li {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    border-bottom: 1px solid #eee;
}

.scan-time {
    color: #666;
    font-size: 0.9em;
}

.scan-data {
    flex: 1;
    margin: 0 10px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.scan-status.printed {
    color: #4CAF50;
}

button {
    padding: 10px 20px;
    background: #2196F3;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.3s;
}

button:hover:not(:disabled) {
    background: #1976D2;
}

button:disabled {
    background: #ccc;
    cursor: not-allowed;
}
</style>