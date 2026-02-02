class ScannerService {
    constructor() {
        this.buffer = ''
        this.timeout = null
        this.callback = null

        // Настройки для сканера Bestson S20-B
        this.SCANNER_CONFIG = {
            suffix: '\r\n',  // Сканер обычно добавляет Enter в конце
            debounceTime: 100 // Время ожидания конца ввода
        }
    }

    // Инициализация слушателя сканера
    init(callback) {
        this.callback = callback

        window.addEventListener('keypress', (e) => {
            this.handleKeyPress(e)
        })

        window.addEventListener('keydown', (e) => {
            this.handleKeyDown(e)
        })
    }

    // Обработка нажатий клавиш
    handleKeyPress(e) {
        // Игнорируем обычный ввод с клавиатуры если это не сканер
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return
        }

        // Добавляем символ в буфер
        this.buffer += e.key

        // Сбрасываем таймер
        if (this.timeout) {
            clearTimeout(this.timeout)
        }

        // Запускаем таймер для определения конца сканирования
        this.timeout = setTimeout(() => {
            this.processBuffer()
        }, this.SCANNER_CONFIG.debounceTime)
    }

    handleKeyDown(e) {
        // Обработка Enter (если сканер отправляет его)
        if (e.key === 'Enter' && this.buffer) {
            if (this.timeout) {
                clearTimeout(this.timeout)
            }
            this.processBuffer()
        }
    }

    // Обработка буфера
    processBuffer() {
        if (!this.buffer) return

        // Убираем суффикс сканера если есть
        let data = this.buffer
        if (this.SCANNER_CONFIG.suffix && data.endsWith(this.SCANNER_CONFIG.suffix)) {
            data = data.slice(0, -this.SCANNER_CONFIG.suffix.length)
        }

        // Вызываем callback с данными
        if (this.callback && data.trim()) {
            this.callback(data.trim())
        }

        // Очищаем буфер
        this.buffer = ''
    }

    // Проверка подключения сканера
    async checkConnection() {
        try {
            // Попытка прочитать с COM порта через API
            const response = await fetch('/api/v1/scanner/check')
            return response.ok
        } catch (error) {
            return false
        }
    }
}

export default new ScannerService()