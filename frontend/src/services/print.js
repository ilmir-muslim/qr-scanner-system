class PrintService {
    constructor() {
        this.printWindow = null
    }

    // Печать QR кода
    async printQRCode(qrImageData, qrData) {
        return new Promise((resolve, reject) => {
            // Создаем окно для печати
            const printWindow = window.open('', '_blank')

            if (!printWindow) {
                reject(new Error('Не удалось открыть окно для печати. Разрешите всплывающие окна.'))
                return
            }

            // Создаем HTML для печати
            const printContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <title>Печать QR кода</title>
          <style>
            @media print {
              body { margin: 0; padding: 0; }
              .print-container { 
                width: 100%; 
                height: 100%; 
                display: flex; 
                flex-direction: column; 
                align-items: center; 
                justify-content: center;
              }
              .qr-code { 
                width: 300px; 
                height: 300px; 
                margin: 20px auto;
              }
              .qr-data {
                font-family: monospace;
                text-align: center;
                margin-top: 10px;
                font-size: 12px;
                word-break: break-all;
                padding: 0 20px;
              }
              .print-date {
                text-align: center;
                font-size: 10px;
                margin-top: 10px;
                color: #666;
              }
            }
            @page {
              margin: 0;
              size: auto;
            }
          </style>
        </head>
        <body>
          <div class="print-container">
            <img class="qr-code" src="${qrImageData}" alt="QR Code" />
            <div class="qr-data">${qrData}</div>
            <div class="print-date">${new Date().toLocaleString()}</div>
          </div>
          <script>
            window.onload = function() {
              window.print();
              setTimeout(function() {
                window.close();
              }, 1000);
            }
          </script>
        </body>
        </html>
      `

            printWindow.document.write(printContent)
            printWindow.document.close()

            printWindow.onbeforeunload = () => {
                resolve()
            }

            // Фолбэк на случай если печать не сработала
            setTimeout(() => {
                if (!printWindow.closed) {
                    printWindow.close()
                    resolve()
                }
            }, 5000)
        })
    }

    // Печать напрямую (если браузер поддерживает)
    printDirect(content) {
        if (window.print) {
            const printContent = document.createElement('div')
            printContent.innerHTML = content
            document.body.appendChild(printContent)
            window.print()
            document.body.removeChild(printContent)
        } else {
            console.warn('Браузер не поддерживает прямую печать')
        }
    }
}

export default new PrintService()