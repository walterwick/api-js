from flask import Flask, render_template_string
import urllib.request as url_request
import json
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>F1 Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                color: #333;
                margin: 0;
                padding: 0;
            }
            h1 {
                text-align: center;
                margin-top: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 20px auto;
                padding: 20px;
                background: #fff;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            .links {
                margin-top: 30px;
            }
            .links a {
                margin: 10px;
                padding: 15px 30px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-size: 18px;
            }
            .links a:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <h1>F1 Dashboard</h1>
        <div class="container">
            <h2>Welcome to the F1 Dashboard</h2>
            <div class="links">
                <a href="/radio">Radyo Mesajları</a>
                <a href="/messages">Race Control Mesajları</a>
            </div>
        </div>
    </body>
    </html>
    """)

@app.route('/radio')
def radio():
    try:
        session_url = 'http://livetiming.formula1.com/static/SessionInfo.json'
        with url_request.urlopen(session_url) as response:
            if response.getcode() == 200:
                session_info = json.loads(response.read().decode('utf-8-sig'))
                base_path = session_info['Path']
            else:
                return "Session info API failed."

        team_radio_url = f'http://livetiming.formula1.com/static/{base_path}TeamRadio.json'
        team_radio_response = requests.get(team_radio_url)
        if team_radio_response.status_code == 200:
            team_radio_data = json.loads(team_radio_response.text.encode('utf-8').decode('utf-8-sig'))
        else:
            team_radio_data = {"Captures": []}

        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Radyo Mesajları</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    color: #333;
                    margin: 0;
                    padding: 0;
                }
                h1, h2 {
                    text-align: center;
                    margin-top: 20px;
                }
                .container {
                    max-width: 1200px;
                    margin: 20px auto;
                    padding: 20px;
                    background: #fff;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                }
                .back-link {
                    text-align: center;
                    margin: 20px;
                }
                .back-link a {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                }
                .back-link a:hover {
                    background-color: #45a049;
                }
                ul {
                    list-style: none;
                    padding: 0;
                }
                li {
                    background-color: #f9f9f9;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 10px;
                    margin-bottom: 10px;
                }
                .buttons button {
                    margin: 5px 0;
                }
            </style>
        </head>
        <body>
            <h1>Radyo Mesajları</h1>
            <div class="container">
                <ul>
        """
        for index, capture in enumerate(team_radio_data.get("Captures", [])):
            full_url = f"http://livetiming.formula1.com/static/{base_path}{capture['Path']}"
            html += f"""
            <li>
                <strong>Racing Number:</strong> {capture['RacingNumber']}<br>
                <strong>UTC:</strong> {capture['Utc']}<br>
                <audio id="audio-{index}" src="{full_url}"></audio>
                <div class="buttons">
                    <button onclick="playAudio({index})">Başlat</button>
                    <button onclick="stopAudio({index})">Durdur</button>
                </div>
            </li>
            """
        html += """
                </ul>
                <div class="back-link">
                    <a href="/">Ana Sayfaya Dön</a>
                </div>
            </div>
            <script>
                let currentAudio = null;

                function playAudio(index) {
                    if (currentAudio) {
                        currentAudio.pause();
                        currentAudio.currentTime = 0;
                    }
                    const audio = document.getElementById(`audio-${index}`);
                    audio.play();
                    currentAudio = audio;
                }

                function stopAudio(index) {
                    const audio = document.getElementById(`audio-${index}`);
                    audio.pause();
                    audio.currentTime = 0;
                    currentAudio = null;
                }
            </script>
        </body>
        </html>
        """
        return html

    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/messages')
def messages():
    try:
        session_url = 'http://livetiming.formula1.com/static/SessionInfo.json'
        with url_request.urlopen(session_url) as response:
            if response.getcode() == 200:
                session_info = json.loads(response.read().decode('utf-8-sig'))
                base_path = session_info['Path']
            else:
                return "Session info API failed."

        race_control_url = f'http://livetiming.formula1.com/static/{base_path}RaceControlMessages.json'
        race_control_response = requests.get(race_control_url)
        if race_control_response.status_code == 200:
            race_control_data = json.loads(race_control_response.text.encode('utf-8').decode('utf-8-sig'))
        else:
            race_control_data = {"Messages": []}

        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Race Control Mesajları</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    color: #333;
                    margin: 0;
                    padding: 0;
                }
                h1, h2 {
                    text-align: center;
                    margin-top: 20px;
                }
                .container {
                    max-width: 1200px;
                    margin: 20px auto;
                    padding: 20px;
                    background: #fff;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                }
                .back-link {
                    text-align: center;
                    margin: 20px;
                }
                .back-link a {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                }
                .back-link a:hover {
                    background-color: #45a049;
                }
                ul {
                    list-style: none;
                    padding: 0;
                }
                li {
                    background-color: #f9f9f9;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 10px;
                    margin-bottom: 10px;
                }
            </style>
        </head>
        <body>
            <h1>Race Control Mesajları</h1>
            <div class="container">
                <ul>
        """
        for message in race_control_data.get("Messages", []):
            html += f"""
            <li>
                <strong>UTC:</strong> {message['Utc']}<br>
                <strong>Lap:</strong> {message['Lap']}<br>
                <strong>Category:</strong> {message['Category']}<br>
                <strong>Message:</strong> {message['Message']}<br>
            """
            if "Flag" in message:
                html += f"<strong>Flag:</strong> {message['Flag']}<br>"
            if "Scope" in message:
                html += f"<strong>Scope:</strong> {message['Scope']}<br>"
            html += "</li>"

        html += """
                </ul>
                <div class="back-link">
                    <a href="/">Ana Sayfaya Dön</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
