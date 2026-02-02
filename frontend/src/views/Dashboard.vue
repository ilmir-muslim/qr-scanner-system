<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>QR Scanner System Dashboard</h1>
      <p>Система сканирования и печати QR кодов</p>
    </div>
    
    <div class="stats">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <h3>Всего сканирований</h3>
          <p class="stat-value">{{ totalScans }}</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🖨️</div>
        <div class="stat-content">
          <h3>Напечатано</h3>
          <p class="stat-value">{{ printedScans }}</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">📷</div>
        <div class="stat-content">
          <h3>Через камеру</h3>
          <p class="stat-value">{{ cameraScans }}</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🔢</div>
        <div class="stat-content">
          <h3>Через сканер</h3>
          <p class="stat-value">{{ scannerScans }}</p>
        </div>
      </div>
    </div>
    
    <div class="quick-actions">
      <h2>Быстрые действия</h2>
      <div class="actions-grid">
        <router-link to="/scan" class="action-card">
          <div class="action-icon">📷</div>
          <h3>Сканировать</h3>
          <p>Сканировать QR код камерой или сканером</p>
        </router-link>
        
        <router-link to="/history" class="action-card">
          <div class="action-icon">📋</div>
          <h3>История</h3>
          <p>Просмотреть историю сканирований</p>
        </router-link>
        
        <div class="action-card" @click="exportHistory">
          <div class="action-icon">📥</div>
          <h3>Экспорт</h3>
          <p>Экспортировать данные в Excel</p>
        </div>
        
        <div class="action-card" @click="togglePrinter">
          <div class="action-icon" :class="{ active: isPrinter }">🖨️</div>
          <h3>{{ isPrinter ? 'Принтер активен' : 'Активировать печать' }}</h3>
          <p>{{ isPrinter ? 'Этот клиент используется для печати' : 'Использовать этот клиент для печати' }}</p>
        </div>
      </div>
    </div>
    
    <div class="recent-activity">
      <h2>Последняя активность</h2>
      <div class="activity-list">
        <div v-for="scan in recentScans" :key="scan.id" class="activity-item">
          <div class="activity-time">{{ formatTime(scan.scanned_at) }}</div>
          <div class="activity-details">
            <div class="activity-type">{{ getScanTypeLabel(scan.scan_type) }}</div>
            <div class="activity-data" :title="scan.qr_data">
              {{ truncateText(scan.qr_data, 50) }}
            </div>
            <div class="activity-status" :class="{ printed: scan.printed }">
              {{ scan.printed ? '✓ Напечатано' : 'В очереди' }}
            </div>
          </div>
        </div>
        
        <div v-if="recentScans.length === 0" class="no-activity">
          <p>Нет данных о сканированиях</p>
        </div>
      </div>
    </div>
    
    <div class="system-info">
      <h2>Информация о системе</h2>
      <div class="info-grid">
        <div class="info-item">
          <strong>Адрес сервера:</strong> {{ serverAddress }}
        </div>
        <div class="info-item">
          <strong>Версия API:</strong> 1.0.0
        </div>
        <div class="info-item">
          <strong>Статус:</strong> <span class="status-online">Online</span>
        </div>
        <div class="info-item">
          <strong>Принтер:</strong> {{ printerStatus }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import { useToast } from '../services/toast'

export default {
  name: 'Dashboard',
  setup() {
    const totalScans = ref(0)
    const printedScans = ref(0)
    const cameraScans = ref(0)
    const scannerScans = ref(0)
    const recentScans = ref([])
    const isPrinter = ref(false)
    const serverAddress = ref(window.location.hostname)
    const printerStatus = ref('Не подключен')
    
    const toast = useToast()
    
    // Загрузка статистики
    async function loadStats() {
      try {
        const scans = await api.getScans(0, 100)
        
        totalScans.value = scans.length
        printedScans.value = scans.filter(s => s.printed).length
        cameraScans.value = scans.filter(s => s.scan_type === 'camera').length
        scannerScans.value = scans.filter(s => s.scan_type === 'scanner').length
        recentScans.value = scans.slice(0, 5)
        
      } catch (error) {
        console.error('Ошибка загрузки статистики:', error)
      }
    }
    
    // Экспорт истории
    async function exportHistory() {
      try {
        await api.exportExcel()
        toast.success('Экспорт завершен успешно')
      } catch (error) {
        toast.error('Ошибка при экспорте')
        console.error(error)
      }
    }
    
    // Переключение принтера
    function togglePrinter() {
      isPrinter.value = !isPrinter.value
      printerStatus.value = isPrinter.value ? 'Активен (этот клиент)' : 'Не подключен'
      
      toast.info(isPrinter.value ? 
        'Этот клиент теперь используется для печати' : 
        'Печать с этого клиента отключена'
      )
    }
    
    // Форматирование времени
    function formatTime(dateString) {
      const date = new Date(dateString)
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
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
    
    // Обрезка текста
    function truncateText(text, maxLength) {
      if (text.length <= maxLength) return text
      return text.substr(0, maxLength) + '...'
    }
    
    onMounted(() => {
      loadStats()
    })
    
    return {
      totalScans,
      printedScans,
      cameraScans,
      scannerScans,
      recentScans,
      isPrinter,
      serverAddress,
      printerStatus,
      exportHistory,
      togglePrinter,
      formatTime,
      getScanTypeLabel,
      truncateText
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
}

.dashboard-header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.dashboard-header p {
  font-size: 1.2rem;
  opacity: 0.9;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 25px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0,0,0,0.15);
}

.stat-icon {
  font-size: 3rem;
  margin-right: 20px;
}

.stat-content h3 {
  font-size: 1rem;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
}

.quick-actions {
  margin-bottom: 40px;
}

.quick-actions h2 {
  margin-bottom: 20px;
  color: #333;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.action-card {
  background: white;
  border-radius: 8px;
  padding: 25px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  text-decoration: none;
  color: inherit;
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0,0,0,0.15);
  background: #f8f9fa;
}

.action-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.action-icon.active {
  color: #4CAF50;
}

.action-card h3 {
  margin-bottom: 10px;
  color: #333;
}

.action-card p {
  color: #666;
  font-size: 0.9rem;
}

.recent-activity {
  margin-bottom: 40px;
}

.recent-activity h2 {
  margin-bottom: 20px;
  color: #333;
}

.activity-list {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.activity-item {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-time {
  min-width: 80px;
  color: #666;
  font-size: 0.9rem;
}

.activity-details {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 20px;
}

.activity-type {
  padding: 4px 12px;
  background: #e3f2fd;
  color: #1976D2;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
}

.activity-data {
  flex: 1;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.activity-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
}

.activity-status.printed {
  background: #e8f5e9;
  color: #388E3C;
}

.activity-status:not(.printed) {
  background: #fff3e0;
  color: #f57c00;
}

.no-activity {
  padding: 40px;
  text-align: center;
  color: #999;
}

.system-info {
  background: white;
  border-radius: 8px;
  padding: 25px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.system-info h2 {
  margin-bottom: 20px;
  color: #333;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.info-item {
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.status-online {
  color: #4CAF50;
  font-weight: bold;
}
</style>
