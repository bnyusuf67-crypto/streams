import requests
import re
import urllib3

urllib3.disable_warnings()

TARGET_URL = "https://www.atvavrupa.tv/canli-yayin"
BACKUP_URL = "https://uzunmuhalefet.unaux.com/trkvz.php?kanal=atvavrupa&.m3u8"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": TARGET_URL
}

def print_clean_m3u8(m3u8_url):
    """HTTP durum kodunu, HTML içeriğini ve m3u8 geçerliliğini kontrol eder."""
    try:
        res = requests.get(m3u8_url, headers=headers, verify=False, timeout=15)
        
        # 1. Katman: 403, 404, 500 gibi sunucu hatalarında anında reddet
        if res.status_code != 200:
            return False

        text = res.text

        # 2. Katman: HTML kodu içeriyorsa veya geçerli m3u8 değilse reddet
        if "<html" in text.lower() or "<body" in text.lower() or "#EXTM3U" not in text:
            return False

        base_url = m3u8_url.rsplit('/', 1)[0] + '/'
        modified_content = ""

        for line in text.splitlines():
            line_str = line.strip()
            if line_str and not line_str.startswith("#"):
                if not line_str.startswith("http"):
                    modified_content += base_url + line_str + "\n"
                else:
                    modified_content += line_str + "\n"
            else:
                modified_content += line + "\n"

        print(modified_content)
        return True
    except Exception:
        return False

def fetch_from_backup():
    """Yedek kaynağa bağlanıp HTML içermeyen temiz m3u8 yayınını getirir."""
    try:
        res = requests.get(BACKUP_URL, headers=headers, verify=False, timeout=15)
        if res.status_code == 200:
            text = res.text

            # Doğrudan m3u8 içeriği döndüyse yazdır
            if "#EXTM3U" in text and "<html" not in text.lower():
                return print_clean_m3u8(BACKUP_URL)

            # HTML kodu döndüyse, içindeki gizli yayın URL'sini süzüp çağır
            matches = re.findall(r'https?://[^\s"\'<>]+(?:trkvz\.php\?[^\s"\'<>]*)', text)
            for target_url in matches:
                if target_url != BACKUP_URL:
                    if print_clean_m3u8(target_url):
                        return True
    except Exception:
        pass
    return False

# --- ANA AKIŞ ---
success = False

try:
    response = requests.get(TARGET_URL, headers=headers, verify=False, timeout=15)
    if response.status_code == 200:
        site_content = response.text
        
        v_match = re.search(r'data-videoid=["\']([^"\']+)["\']', site_content)
        w_match = re.search(r'data-websiteid=["\']([^"\']+)["\']', site_content)

        if v_match and w_match:
            video_id = v_match.group(1)
            website_id = w_match.group(1)

            getvideo_url = f"https://videojs.tmgrup.com.tr/getvideo/{website_id}/{video_id}"
            video_res = requests.get(getvideo_url, headers=headers, verify=False, timeout=15)

            if video_res.status_code == 200 and video_res.json().get("success"):
                raw_hls_url = video_res.json()["video"]["VideoSmilUrl"]

                secure_api = "https://securevideotoken.tmgrup.com.tr/webtv/secure"
                token_res = requests.get(secure_api, params={"url": raw_hls_url}, headers=headers, verify=False, timeout=15)

                if token_res.status_code == 200 and token_res.json().get("Success"):
                    secure_hls_url = token_res.json().get("Url")
                    # Token URL'si 403/404 verirse print_clean_m3u8 False dönecektir
                    success = print_clean_m3u8(secure_hls_url)
except Exception:
    pass

# Ana kaynak hata verdiğinde (403, 404, geçersiz link vb.) yedeğe geçer
if not success:
    fetch_from_backup()
