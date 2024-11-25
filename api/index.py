from flask import Flask, render_template_string, request
import requests
import json
from datetime import datetime, timedelta

app = Flask(__name__)

class WeatherAPI:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://www.mgm.gov.tr/",
            "Origin": "https://www.mgm.gov.tr",
            "Connection": "keep-alive"
        }
    
    def _make_request(self, url, use_headers=True):
        try:
            response = requests.get(
                url, 
                headers=self.headers if use_headers else None, 
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API isteği başarısız: {url} - {str(e)}")
            return None

class LocationService:
    @staticmethod
    def clear_tr_chars(text):
        if not text:
            return ""
        tr_chars = str.maketrans("ıİçÇğĞöÖşŞüÜ", "iIcCggOoSsUu")
        return text.translate(tr_chars)

class TurkeyWeatherAPI(WeatherAPI):
    def __init__(self, province_name, district_name=None):
        super().__init__()
        self.province_name = province_name
        self.district_name = district_name
        self.location_details = None
        self.weather_details = None
        self.sunrise = None
        self.sunset = None
        self.fetch_data()

    def fetch_data(self):
        self._fetch_location()
        if not self.location_details:
            raise ValueError("Lokasyon bilgileri alınamadı")

        self._fetch_weather()
        self._fetch_sun_times()

    def _fetch_location(self):
        province = LocationService.clear_tr_chars(self.province_name)
        district = LocationService.clear_tr_chars(self.district_name) if self.district_name else ''
        provinces = self._make_request("https://servis.mgm.gov.tr/web/merkezler/iller")
        if not provinces:
            raise ValueError("İl listesi alınamadı")
        province_info = next(
            (p for p in provinces if LocationService.clear_tr_chars(p['il']).lower() == province.lower()),
            None
        )
        if not province_info:
            raise ValueError(f"'{self.province_name}' ili bulunamadı")
        districts = self._make_request(
            f"https://servis.mgm.gov.tr/web/merkezler/ililcesi?il={province_info['il']}"
        )
        if not districts:
            raise ValueError("İlçe listesi alınamadı")
        if district:
            self.location_details = next(
                (d for d in districts if LocationService.clear_tr_chars(d['ilce']).lower() == district.lower()),
                districts[0]
            )
        else:
            self.location_details = districts[0]

    def _fetch_weather(self):
        if not self.location_details:
            return
        weather_data = self._make_request(
            f"https://servis.mgm.gov.tr/web/sondurumlar?merkezid={self.location_details['merkezId']}"
        )
        if weather_data and len(weather_data) > 0:
            self.weather_details = weather_data[0]

    def _fetch_sun_times(self):
        if not self.location_details:
            return
        sun_data = self._make_request(
            f"https://api.sunrise-sunset.org/json?lat={self.location_details['enlem']}&lng={self.location_details['boylam']}&formatted=0",
            use_headers=False
        )
        if sun_data and sun_data.get('status') == 'OK':
            self.sunrise = datetime.fromisoformat(
                sun_data['results']['sunrise'].replace('Z', '+00:00')
            ).astimezone() + timedelta(hours=3)
            self.sunset = datetime.fromisoformat(
                sun_data['results']['sunset'].replace('Z', '+00:00')
            ).astimezone() + timedelta(hours=3)

    def get_all_data(self):
        if not self.weather_details:
            return None
        return {
            'location': {
                'province': self.location_details.get('il', 'N/A'),
                'district': self.location_details.get('ilce', 'N/A'),
                'latitude': self.location_details.get('enlem', 'N/A'),
                'longitude': self.location_details.get('boylam', 'N/A')
            },
            'current_weather': {
                'temperature': self.weather_details.get('sicaklik', 'N/A'),
                'humidity': self.weather_details.get('nem', 'N/A'),
                'pressure': self.weather_details.get('aktuelBasinc', 'N/A'),
                'wind_speed': self.weather_details.get('ruzgarHiz', 'N/A'),
            },
            'sun_times': {
                'sunrise': self.sunrise.strftime("%H:%M") if self.sunrise else 'N/A',
                'sunset': self.sunset.strftime("%H:%M") if self.sunset else 'N/A'
            },
        }

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Hava Durumu</title>
</head>
<body>
    <h1>Hava Durumu</h1>
    <form method="GET" action="/">
        İl: <input type="text" name="province" value="{{ province }}" required><br>
        İlçe: <input type="text" name="district" value="{{ district }}"><br>
        <button type="submit">Sorgula</button>
    </form>
    {% if weather %}
        <h2>Sonuçlar:</h2>
        <p>İl: {{ weather['location']['province'] }}</p>
        <p>İlçe: {{ weather['location']['district'] }}</p>
        <p>Sıcaklık: {{ weather['current_weather']['temperature'] }}°C</p>
        <p>Nem: {{ weather['current_weather']['humidity'] }}%</p>
        <p>Basınç: {{ weather['current_weather']['pressure'] }} hPa</p>
        <p>Rüzgar Hızı: {{ weather['current_weather']['wind_speed'] }} km/h</p>
        <p>Gün Doğumu: {{ weather['sun_times']['sunrise'] }}</p>
        <p>Gün Batımı: {{ weather['sun_times']['sunset'] }}</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", defaults={"province": "şanlıurfa", "district": "karaköprü"})
@app.route("/<province>", defaults={"district": None})
@app.route("/<province>?<district>")
def index(province, district):
    province = request.args.get("province", province)
    district = request.args.get("district", district)
    weather = None
    try:
        weather_api = TurkeyWeatherAPI(province, district)
        weather = weather_api.get_all_data()
    except Exception as e:
        weather = {"error": str(e)}
    return render_template_string(HTML_TEMPLATE, weather=weather, province=province, district=district or "")

if __name__ == "__main__":
    app.run(debug=True)
