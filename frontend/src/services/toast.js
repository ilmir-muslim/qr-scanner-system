// Простой сервис уведомлений
export const useToast = () => {
  const show = (message, type = 'info') => {
    // Создаем элемент уведомления
    const toast = document.createElement('div')
    toast.className = `notification ${type}`
    toast.textContent = message
    
    // Добавляем в DOM
    document.body.appendChild(toast)
    
    // Удаляем через 3 секунды
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast)
      }
    }, 3000)
  }
  
  return {
    info: (message) => show(message, 'info'),
    success: (message) => show(message, 'success'),
    error: (message) => show(message, 'error'),
    warning: (message) => show(message, 'warning')
  }
}

export default useToast
