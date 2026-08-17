import requests
import json

def get_m3u8_link(api_url, x_forwarded_for):
    headers = {
        'X-Forwarded-For': x_forwarded_for
    }

    # API'den veriyi çek
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    data = response.json()

    # JSON içerisinden ilgili link parçalarını al
    service_url = data["Media"]["Link"]["ServiceUrl"]
    secure_path = data["Media"]["Link"]["SecurePath"]

    # Unicode kaçış dizilerini düzelt
    secure_path = secure_path.encode('utf-8').decode('unicode_escape')

    # Bağlantıyı birleştir
    final_m3u8_link = f"{service_url}{secure_path}"

    return final_m3u8_link

api_url = "https://www.cnnturk.com/api/cnnvideo/media?id=62d6814670380e2cdc7c124c&isMobile=true"
x_forwarded_for = "0.0.0.0"

try:
    m3u8_link = get_m3u8_link(api_url, x_forwarded_for)
    # Metni f-string tırnakları içerisine alarak yazdırıyoruz:
    print(f"#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=7680000\n{m3u8_link}")
except Exception as e:
    print(f"Error: {e}")
