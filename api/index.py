from flask import Flask, render_template_string, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

# Başsız modda tarayıcı başlatma ayarları
def get_card_info(card_number):
    options = Options()
    options.add_argument('--headless')  # Başsız modda çalışmasını sağlar
    options.add_argument('--disable-gpu')  # GPU'yu devre dışı bırakır (özellikle başsız modda)

    # WebDriver'ı başlat
    service = Service(ChromeDriverManager().install())  # ChromeDriver'ı otomatik olarak indirir
    driver = webdriver.Chrome(service=service, options=options)

    # Siteye git
    driver.get('https://ulasim.urfakart.com/bakiye-sorgulama/')
    time.sleep(2)

    # Pop-up varsa, Tab tuşuna basarak pop-up'a geçiş yap ve Enter tuşuna bas
    try:
        actions = webdriver.ActionChains(driver)
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.5)  # Tab tuşundan sonra küçük bir bekleme
        actions.send_keys(Keys.RETURN).perform()  # Pop-up'ı kapat
    except Exception as e:
        print("Pop-up kapatma işlemi sırasında hata oluştu:", e)

    # Input alanına veri yazmadan önce input öğesinin etkileşimli olmasını bekle
    input_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'input-47'))
    )

    # Input alanına kart numarasını yaz
    input_element.send_keys(card_number)

    # Enter tuşuna bas
    input_element.send_keys(Keys.RETURN)

    # Sayfa yüklenene kadar bekle (dinamik içerik için)
    time.sleep(3)

    # Sonuçları al: Tüm <div> öğesinin içeriğini almak için
    try:
        result_div = driver.find_element(By.CLASS_NAME, 'v-card')
        result = result_div.text
    except Exception as e:
        result = "Sonuç alınırken hata oluştu"

    # Tarayıcıyı kapat
    driver.quit()

    return result

# Ana sayfa route'u
@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Kart Bilgisi Sorgulama</title>
        </head>
        <body>
            <h1>Kart Bilgisi Sorgulama</h1>
            <form action="/get_card_info" method="POST">
                <label for="card_number">Kart Numarası:</label>
                <input type="text" id="card_number" name="card_number" required>
                <button type="submit">Sorgula</button>
            </form>

            <div id="result">
                <!-- Sonuç burada gösterilecek -->
            </div>

            <script>
                // Formu gönderdiğinde sonucu alıp, sayfada göstermek
                const form = document.querySelector('form');
                form.addEventListener('submit', async (event) => {
                    event.preventDefault();
                    const formData = new FormData(form);
                    const response = await fetch('/get_card_info', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();
                    document.getElementById('result').innerText = data.result;
                });
            </script>
        </body>
        </html>
    ''')

# Kart sorgulama route'u
@app.route('/get_card_info', methods=['POST'])
def get_card_info_route():
    card_number = request.form['card_number']
    result = get_card_info(card_number)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
