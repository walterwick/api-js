from flask import Flask, render_template, redirect, request, jsonify
from io import BytesIO
import requests
from instaloader import Instaloader, Profile
import base64
import os

app = Flask(__name__)

# Çerez dosyasının yolu
COOKIE_FILE = "insta_session"

# Instaloader nesnesi oluştur
insta = Instaloader()

# Oturum açma fonksiyonu
def login_to_instagram(username, password):
    if os.path.exists(COOKIE_FILE):
        # Eğer çerez dosyası varsa, onu yükle
        insta.load_session_from_file(username, COOKIE_FILE)
        print("Oturum çerezden yüklendi.")
    else:
        # Çerez yoksa oturum aç ve çerezi kaydet
        insta.login(username, password)
        insta.save_session_to_file(COOKIE_FILE)
        print("Yeni oturum açıldı ve çerez kaydedildi.")

# Instagram'a giriş yap
login_to_instagram('walterw6770', 'ws7ca7p7')

@app.route("/")
def index():
    # Yönlendirmeyi geçici olarak devre dışı bırakmak için yorum satırı ekleyin
    # return render_template("index.html")

    # Kullanıcıyı doğrudan profile yönlendir
    return redirect("/profile?username=emineey41")

@app.route("/profile")
def profile():
    username = request.args.get("username")

    if username:
        try:
            profile = Profile.from_username(insta.context, username)

            # Profile information dictionary
            data = {
                "username": profile.username,
                "post_count": profile.mediacount,
                "followers": profile.followers,
                "followees": profile.followees,
                "bio": profile.biography,
                "profile_pic_url": profile.profile_pic_url,
                "full_name": profile.full_name,  # Might not always be available
            }

            # Profil resmini Base64 formatına çevirerek HTML içinde görüntülemek için
            response = requests.get(data["profile_pic_url"])
            profile_pic_base64 = base64.b64encode(response.content).decode('utf-8')

            # HTML olarak parse ederek profil bilgilerini ve resmi göster
            html_content = f"""
            <!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Instagram Profil Bilgileri</title>
    <link rel="shortcut icon" href="data:image/jpeg;base64,{ profile_pic_base64 }" type="image/x-icon">

</head>

<body>

  <div class="data">
            <h1>Instagram Profil Bilgileri '{data['full_name']}'</h1>
            <h2>Kullanıcı Adı: {data['username']}</h2>
            <p>Gönderi Sayısı: {data['post_count']}</p>
            <p>Takipçiler: {data['followers']}</p>
            <p>Takip Edilenler: {data['followees']}</p>
            <p>Biyografi: {data['bio']}</p>
            <p>Tam Ad:{data['full_name']}</p>
            <a href="{data['profile_pic_url']}">pfp</a>
            <img src="data:image/jpeg;base64,{profile_pic_base64}" alt="Profil Resmi">
             </div>

  <style>
    h1 {{
      color: blue
    }}
  </style>

</body>

</html>

            """

            return html_content

        except Exception as e:
            # Handle errors gracefully
            return f"Hata: {str(e)}"
    else:
        return "Kullanıcı adı eksik & hatalı"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000) #host parametresi diğer ip'lerden erişmek için
