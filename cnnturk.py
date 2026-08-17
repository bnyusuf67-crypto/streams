import requests
import re
import json

# Gerçek tarayıcı taklidi yapmak 403 hatalarını önler
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Forwarded-For': '185.125.100.1' # Rastgele bir Türkiye IP adresi
}

def get_from_api(api_url):
    """Ana API üzerinden bağlantıyı almayı dener."""
    response = requests.get(api_url, headers=HEADERS, timeout=10)
    response.raise_for_status() # 4xx veya 5xx hatasında HTTPError fırlatır
    data = response.json()

    service_url = data["Media"]["Link"]["ServiceUrl"]
    secure_path = data["Media"]["Link"]["SecurePath"].encode('utf-8').decode('unicode_escape')
    return f"{service_url}{secure_path}"

def get_from_web_fallback(web_url):
    """API çökerse canlı yayın web sayfasının kaynak kodundan m3u8 bulur."""
    response = requests.get(web_url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    
    # HTML içerisindeki .m3u8 uzantılı URL pattern'ini arar
    pattern = r'https?://[^\s"\']+\.m3u8[^\s"\']*'
    matches = re.findall(pattern, response.text)
    
    if matches:
        # Yakalanan ilk m3u8 linkini döndür
        return matches[0]
    else:
        raise Exception("Web sayfasında m3u8 bağlantısı bulunamadı.")

def main():
    api_url = "https://www.cnnturk.com/api/cnnvideo/media?id=62d6814670380e2cdc7c124c&isMobile=true"
    web_url = "https://www.cnnturk.com/canli-yayin"
    
    m3u8_link = None

    # 1. Aşama: API Denemesi
    try:
        m3u8_link = get_from_api(api_url)
    except (requests.exceptions.HTTPError, Exception) as e:
        # API 403, 404, 500 hatası verirse veya çökerse buraya düşer
        # 2. Aşama: Web Fallback Denemesi
        try:
            m3u8_link = get_from_web_fallback(web_url)
        except Exception as fallback_error:
            print(f"Hata: Hem API hem de Web Fallback başarısız oldu. API Hatası: {e} | Web Hatası: {fallback_error}")
            return

    # Başarılı olursa çıktıyı formatla
    if m3u8_link:
        print(f"#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=7680000\n{m3u8_link}")

if __name__ == "__main__":
    main()
