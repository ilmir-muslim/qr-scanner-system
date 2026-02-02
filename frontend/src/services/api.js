import axios from 'axios'

const API_BASE_URL = '/api/v1'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
})

export default {
    // Сканирование из изображения
    async scanFromImage(imageData, clientId = null) {
        const response = await api.post('/scans/scan-from-image/', {
            image_data: imageData,
            client_id: clientId
        })
        return response.data
    },

    // Создание скана
    async createScan(scanData) {
        const response = await api.post('/scans/scan/', scanData)
        return response.data
    },

    // Ручной ввод (для сканера)
    async manualScan(data, scanType = 'scanner') {
        const response = await api.post('/scans/manual-scan/', null, {
            params: { data, scan_type: scanType }
        })
        return response.data
    },

    // Получение списка сканов
    async getScans(skip = 0, limit = 100, startDate = null, endDate = null) {
        const params = { skip, limit }
        if (startDate) params.start_date = startDate
        if (endDate) params.end_date = endDate

        const response = await api.get('/scans/', { params })
        return response.data
    },

    // Генерация QR кода
    async generateQRCode(data, size = 10) {
        const response = await api.get(`/scans/generate-qr/${data}`, {
            params: { size }
        })
        return `data:image/png;base64,${response.data.qr_image}`
    },

    // Экспорт в Excel
    async exportExcel(startDate = null, endDate = null) {
        const params = {}
        if (startDate) params.start_date = startDate
        if (endDate) params.end_date = endDate

        const response = await api.get('/scans/export-excel/', { params })

        // Скачивание файла
        const link = document.createElement('a')
        link.href = `data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,${response.data.data}`
        link.download = response.data.filename
        link.click()

        return response.data
    }
}