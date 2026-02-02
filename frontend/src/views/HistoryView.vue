<template>
    <div class="history-container">
        <h1>История сканирований</h1>

        <div class="filters">
            <div class="date-filter">
                <label>С:</label>
                <input type="date" v-model="startDate" />
                <label>По:</label>
                <input type="date" v-model="endDate" />
                <button @click="applyFilters">Применить</button>
                <button @click="resetFilters">Сбросить</button>
            </div>

            <div class="export-section">
                <button @click="exportToExcel" class="export-btn">
                    📥 Экспорт в Excel
                </button>
            </div>
        </div>

        <div class="history-table">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Данные QR</th>
                        <th>Тип</th>
                        <th>Время сканирования</th>
                        <th>Статус печати</th>
                        <th>Принтер</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="scan in scans" :key="scan.id">
                        <td>{{ scan.id }}</td>
                        <td class="qr-data">{{ scan.qr_data }}</td>
                        <td>
                            <span class="scan-type" :class="scan.scan_type">
                                {{ getScanTypeLabel(scan.scan_type) }}
                            </span>
                        </td>
                        <td>{{ formatDateTime(scan.scanned_at) }}</td>
                        <td>
                            <span class="print-status" :class="{ printed: scan.printed }">
                                {{ scan.printed ? '✓ Напечатано' : '○ В очереди' }}
                                <br>
                                <small v-if="scan.printed_at">
                                    {{ formatDateTime(scan.printed_at) }}
                                </small>
                            </span>
                        </td>
                        <td>{{ scan.printer_id || '—' }}</td>
                        <td class="actions">
                            <button @click="viewQRCode(scan.qr_data)" title="Просмотреть QR">
                                👁️
                            </button>
                            <button @click="reprint(scan)" title="Печать" v-if="!scan.printed">
                                🖨️
                            </button>
                            <button @click="deleteScan(scan.id)" title="Удалить" class="delete">
                                🗑️
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>

            <div v-if="loading" class="loading">
                Загрузка...
            </div>

            <div v-if="scans.length === 0 && !loading" class="no-data">
                Нет данных для отображения
            </div>

            <div class="pagination" v-if="totalPages > 1">
                <button @click="prevPage" :disabled="currentPage === 1">
                    Назад
                </button>
                <span>Страница {{ currentPage }} из {{ totalPages }}</span>
                <button @click="nextPage" :disabled="currentPage === totalPages">
                    Вперед
                </button>
            </div>
        </div>

        <!-- Модальное окно просмотра QR -->
        <div v-if="showQRModal" class="modal-overlay" @click="closeQRModal">
            <div class="modal-content" @click.stop>
                <button class="close-btn" @click="closeQRModal">×</button>
                <h3>QR код</h3>
                <img :src="currentQRCode" alt="QR Code" />
                <p class="qr-data-modal">{{ currentQRData }}</p>
                <button @click="printCurrentQR" class="print-btn">
                    🖨️ Печатать
                </button>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useToast } from '../services/toast'
import api from '../services/api'
import printService from '../services/print'

export default {
    name: 'HistoryView',
    setup() {
        const scans = ref([])
        const loading = ref(false)
        const currentPage = ref(1)
        const pageSize = ref(20)
        const totalScans = ref(0)
        const startDate = ref('')
        const endDate = ref('')
        const showQRModal = ref(false)
        const currentQRCode = ref('')
        const currentQRData = ref('')

        const totalPages = computed(() => {
            return Math.ceil(totalScans.value / pageSize.value)
        })

        // Загрузка данных
        async function loadScans() {
            loading.value = true

            try {
                const response = await api.getScans(
                    (currentPage.value - 1) * pageSize.value,
                    pageSize.value,
                    startDate.value || null,
                    endDate.value || null
                )

                scans.value = response
                // В реальном API нужно получать общее количество
                totalScans.value = response.length * totalPages.value

            } catch (error) {
                useToast().error('Ошибка загрузки истории')
                console.error(error)
            } finally {
                loading.value = false
            }
        }

        // Применение фильтров
        function applyFilters() {
            currentPage.value = 1
            loadScans()
        }

        // Сброс фильтров
        function resetFilters() {
            startDate.value = ''
            endDate.value = ''
            currentPage.value = 1
            loadScans()
        }

        // Пагинация
        function nextPage() {
            if (currentPage.value < totalPages.value) {
                currentPage.value++
                loadScans()
            }
        }

        function prevPage() {
            if (currentPage.value > 1) {
                currentPage.value--
                loadScans()
            }
        }

        // Экспорт в Excel
        async function exportToExcel() {
            try {
                await api.exportExcel(
                    startDate.value || null,
                    endDate.value || null
                )
                useToast().success('Файл успешно экспортирован')
            } catch (error) {
                useToast().error('Ошибка при экспорте')
                console.error(error)
            }
        }

        // Просмотр QR кода
        async function viewQRCode(qrData) {
            currentQRData.value = qrData
            currentQRCode.value = await api.generateQRCode(qrData)
            showQRModal.value = true
        }

        function closeQRModal() {
            showQRModal.value = false
            currentQRCode.value = ''
            currentQRData.value = ''
        }

        // Повторная печать
        async function reprint(scan) {
            try {
                const qrImage = await api.generateQRCode(scan.qr_data)
                await printService.printQRCode(qrImage, scan.qr_data)
                useToast().success('Повторная печать запущена')
            } catch (error) {
                useToast().error('Ошибка при печати')
                console.error(error)
            }
        }

        // Удаление скана
        async function deleteScan(scanId) {
            if (!confirm('Удалить эту запись?')) return

            try {
                // В реальном API нужно добавить endpoint для удаления
                useToast().info('Функция удаления в разработке')
            } catch (error) {
                useToast().error('Ошибка при удалении')
            }
        }

        // Печать текущего QR кода
        async function printCurrentQR() {
            try {
                await printService.printQRCode(currentQRCode.value, currentQRData.value)
                closeQRModal()
            } catch (error) {
                useToast().error('Ошибка при печати')
            }
        }

        // Форматирование даты
        function formatDateTime(dateString) {
            const date = new Date(dateString)
            return date.toLocaleString()
        }

        // Метка типа сканирования
        function getScanTypeLabel(type) {
            const labels = {
                'camera': 'Камера',
                'scanner': 'Сканер',
                'manual': 'Вручную'
            }
            return labels[type] || type
        }

        onMounted(() => {
            loadScans()
        })

        return {
            scans,
            loading,
            currentPage,
            totalPages,
            startDate,
            endDate,
            showQRModal,
            currentQRCode,
            currentQRData,

            applyFilters,
            resetFilters,
            nextPage,
            prevPage,
            exportToExcel,
            viewQRCode,
            closeQRModal,
            reprint,
            deleteScan,
            printCurrentQR,
            formatDateTime,
            getScanTypeLabel
        }
    }
}
</script>

<style scoped>
.history-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

.filters {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding: 20px;
    background: #f5f5f5;
    border-radius: 8px;
}

.date-filter {
    display: flex;
    align-items: center;
    gap: 10px;
}

.date-filter label {
    font-weight: bold;
}

.date-filter input {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.export-btn {
    padding: 10px 20px;
    background: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
}

.history-table {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

thead {
    background: #2196F3;
    color: white;
}

th,
td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

.qr-data {
    max-width: 300px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-family: monospace;
}

.scan-type {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8em;
    font-weight: bold;
}

.scan-type.camera {
    background: #E3F2FD;
    color: #1976D2;
}

.scan-type.scanner {
    background: #E8F5E9;
    color: #388E3C;
}

.scan-type.manual {
    background: #FFF3E0;
    color: #F57C00;
}

.print-status {
    padding: 4px 8px;
    border-radius: 4px;
}

.print-status.printed {
    background: #E8F5E9;
    color: #388E3C;
}

.actions {
    display: flex;
    gap: 5px;
}

.actions button {
    padding: 5px 10px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    background: #f5f5f5;
}

.actions button:hover {
    background: #e0e0e0;
}

.actions button.delete {
    color: #f44336;
}

.loading,
.no-data {
    text-align: center;
    padding: 40px;
    font-size: 18px;
    color: #666;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    margin-top: 20px;
    padding: 20px;
}

.pagination button {
    padding: 10px 20px;
    border: 1px solid #ddd;
    background: white;
    border-radius: 4px;
    cursor: pointer;
}

.pagination button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Модальное окно */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    padding: 30px;
    border-radius: 8px;
    max-width: 500px;
    width: 90%;
    position: relative;
    text-align: center;
}

.close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #666;
}

.modal-content h3 {
    margin-bottom: 20px;
}

.modal-content img {
    width: 300px;
    height: 300px;
    margin: 20px auto;
    border: 1px solid #ddd;
}

.qr-data-modal {
    background: #f5f5f5;
    padding: 15px;
    border-radius: 4px;
    word-break: break-all;
    font-family: monospace;
    margin: 20px 0;
}

.print-btn {
    padding: 10px 30px;
    background: #2196F3;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
}
</style>