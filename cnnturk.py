import requests
import sys
import random

def get_random_tr_ip():
    """Türkiye IP bloklarından rastgele bir IP üretir."""
    tr_subnets = [
        "176.234", "88.255", "78.160", "212.252", "85.105"
    ]
    subnet = random.choice(tr_subnets)
    return f"{subnet}.{random.randint(1, 254)}.{random.randint(1, 254)}"

def get_m3u8_link():
    api_url = "https://www.cnnturk.com/api/cnnvideo/media?id=62d6814670380e2cdc7c124c&isMobile=true"
    fake_tr_ip = get_random_tr_ip()

    headers = {
        'User-Agent': 'com.cnnturk/4.1.0 (Android; 12)',
        'X-Forwarded-For': fake_tr_ip,
        'Client-IP': fake_tr_ip
    }

    response = requests.get(api_url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()

    service_url = data["Media"]["Link"]["ServiceUrl"] or data["Media"]["Link"]["DefaultServiceUrl"]
    secure_path = data["Media"]["Link"]["SecurePath"].encode('utf-8').decode('unicode_escape')

    return f"{service_url}{secure_path}"

if __name__ == "__main__":
    try:
        m3u8_link = get_m3u8_link()
        # Sadece M3U8 içeriği stdout'a basılır (dosyaya yazılacak kısım)
        print(f"#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=7680000\n{m3u8_link}")
    except Exception as e:
        # Hata oluşursa M3U8 dosyasını kirletmemek için hatayı stderr'e basıyoruz
        sys.stderr.write(f"HATA: {e}\n")
        sys.exit(1)
