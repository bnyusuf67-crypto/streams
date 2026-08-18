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

def get_latest_segment_from_quality(m3u8_url, target_quality="_576p"):
    """
    Ana m3u8 (Master Playlist) içerisinden hedef kaliteyi (örn: _576p, _360p) seçer,
    alt m3u8 dosyasına girerek en güncel .ts segment adresini bulur.
    """
    try:
        res = requests.get(m3u8_url, headers=headers, verify=False, timeout=10)
        if res.status_code != 200:
            return None

        text = res.text
        if "#EXTM3U" not in text:
            return None

        base_url = m3u8_url.rsplit('/', 1)[0] + '/'
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        selected_sub_playlist = None

        # 1. Aşama: Master listede hedef kalitenin m3u8 adresini ara
        for i, line in enumerate(lines):
            if target_quality in line:
                if not line.startswith("#"):
                    selected_sub_playlist = line
                elif i + 1 < len(lines) and not lines[i + 1].startswith("#"):
                    selected_sub_playlist = lines[i + 1]
                break

        # Hedef kalite bulunamazsa ilk m3u8 uzantılı alternatifi seç
        if not selected_sub_playlist:
            for line in lines:
                if line.endswith(".m3u8") and not line.startswith("#"):
                    selected_sub_playlist = line
                    break

        if not selected_sub_playlist:
            return None

        # Alt m3u8 adresini tam URL yap
        if not selected_sub_playlist.startswith("http"):
            selected_sub_playlist = base_url + selected_sub_playlist

        # 2. Aşama: Seçilen alt m3u8 dosyasını indir
        sub_res = requests.get(selected_sub_playlist, headers=headers, verify=False, timeout=10)
        if sub_res.status_code != 200:
            return None

        sub_text = sub_res.text
        sub_base_url = selected_sub_playlist.rsplit('/', 1)[0] + '/'
        
        # Sadece gerçek segment satırlarını filtrele
        segment_lines = [line.strip() for line in sub_text.splitlines() if line.strip() and not line.strip().startswith("#")]

        if not segment_lines:
            return None

        # 3. Aşama: Alt listedeki en son (en güncel) segmenti al
        target_index = -1
        last_segment = segment_lines[target_index]
        
        if not last_segment.startswith("http"):
            last_segment = sub_base_url + last_segment

        return last_segment

    except Exception:
        return None

def process_stream(m3u8_url):
    """M3U8 yayınını temizler, playlist.m3u ve segment.txt dosyalarına kaydeder."""
    try:
        res = requests.get(m3u8_url, headers=headers, verify=False, timeout=10)
        if res.status_code != 200:
            return False

        text = res.text
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

        # 1. Temizlenmiş m3u8 listesini dosyaya yaz
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write(modified_content)

        # İstediğin kaliteyi buradan değiştirebilirsin (Örn: "_576p", "_360p", "_720p")
        desired_quality = "_576p"
        
        # 2. En güncel segmenti bul ve ayrı bir dosyaya yaz
        latest_seg = get_latest_segment_from_quality(m3u8_url, target_quality=desired_quality)
        if latest_seg:
            with open("segment.txt", "w", encoding="utf-8") as f:
                f.write(latest_seg)
            print(f"Başarılı! 'playlist.m3u' ve 'segment.txt' ({desired_quality}) güncellendi.")
        else:
            print("Playlist kaydedildi ancak segment bulunamadı.")
            
        return True
    except Exception:
        return False

def fetch_from_backup():
    """HTML koduna girmeden doğrudan yedek adresten yayını çekmeye çalışır."""
    try:
        res = requests.get(BACKUP_URL, headers=headers, verify=False, timeout=10)
        if res.status_code == 200:
            text = res.text

            if "#EXTM3U" in text and "<html" not in text.lower():
                return process_stream(BACKUP_URL)

            matches = re.findall(r'https?://[^\s"\'<>]+(?:trkvz\.php\?[^\s"\'<>]*)', text)
            for target_url in matches:
                if target_url != BACKUP_URL:
                    if process_stream(target_url):
                        return True
    except Exception:
        pass
    return False

def fetch_from_main_site():
    """Yedek başarısız olursa ana sitenin HTML, API ve securevideotoken akışını çalıştırır."""
    try:
        response = requests.get(TARGET_URL, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            site_content = response.text
            
            v_match = re.search(r'data-videoid=["\']([^"\']+)["\']', site_content)
            w_match = re.search(r'data-websiteid=["\']([^"\']+)["\']', site_content)

            if v_match and w_match:
                video_id = v_match.group(1)
                website_id = w_match.group(1)

                getvideo_url = f"https://videojs.tmgrup.com.tr/getvideo/{website_id}/{video_id}"
                video_res = requests.get(getvideo_url, headers=headers, verify=False, timeout=10)

                if video_res.status_code == 200 and video_res.json().get("success"):
                    raw_hls_url = video_res.json()["video"]["VideoSmilUrl"]

                    secure_api = "https://securevideotoken.tmgrup.com.tr/webtv/secure"
                    token_res = requests.get(secure_api, params={"url": raw_hls_url}, headers=headers, verify=False, timeout=10)

                    if token_res.status_code == 200 and token_res.json().get("Success"):
                        secure_hls_url = token_res.json().get("Url")
                        return process_stream(secure_hls_url)
    except Exception:
        pass
    return False

# --- ÇALIŞTIRMA AKIŞI ---
success = fetch_from_backup()

if not success:
    fetch_from_main_site()
