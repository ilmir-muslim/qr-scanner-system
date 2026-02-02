<template>
  <div id="app">
    <nav v-if="!isScanPage">
      <router-link to="/">Главная</router-link>
      <router-link to="/scan">Сканирование</router-link>
      <router-link to="/history">История</router-link>
    </nav>
    <main>
      <router-view />
    </main>
    <div v-if="notification.show" class="notification" :class="notification.type">
      {{ notification.message }}
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const route = useRoute()
    const notification = ref({ show: false, message: '', type: 'info' })

    const isScanPage = computed(() => route.name === 'Scan')

    const showNotification = (message, type = 'info') => {
      notification.value = { show: true, message, type }
      setTimeout(() => {
        notification.value.show = false
      }, 3000)
    }

    return {
      isScanPage,
      notification,
      showNotification
    }
  }
}
</script>

<style scoped>
nav {
  background: #333;
  padding: 1rem;
  display: flex;
  gap: 1rem;
}

nav a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

nav a:hover {
  background: #555;
}

.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 1rem;
  border-radius: 4px;
  color: white;
  z-index: 1000;
}

.notification.info {
  background: #2196F3;
}

.notification.success {
  background: #4CAF50;
}

.notification.error {
  background: #f44336;
}
</style>