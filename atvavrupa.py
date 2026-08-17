import requests
import re
import urllib3

urllib3.disable_warnings()

TARGET_URL = "https://www.atvavrupa.tv/canli-yayin"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": TARGET_URL
}

response = requests.get(TARGET_URL, headers=headers, verify=False, timeout=15)

if response.status_code == 200:
    site_content = response.text

    # HTML veya JS değişkeni (tmdPlayer) içerisinden video_id ve website_id değerlerini bulur
    video_id_match = re.search(r'data-videoid=["\']([^"\']+)["\']', site_content)
    website_id_match = re.search(r'data-websiteid=["\']([^"\']+)["\']', site_content)

    if video_id_match and website_id_match:
        video_id = video_id_match.group(1)
        website_id = website_id_match.group(1)

        # 1. Aşama: Video servisinden Smil/HLS URL bilgisini al
        getvideo_url = f"https://videojs.tmgrup.com.tr/getvideo/{website_id}/{video_id}"
        video_res = requests.get(getvideo_url, headers=headers, verify=False)

        if video_res.status_code == 200:
            try:
                video_data = video_res.json()
                if video_data.get("success"):
                    raw_hls_url = video_data["video"]["VideoSmilUrl"]

                    # 2. Aşama: Turkuvaz secure token servisine istek atarak imzalı canlı yayın URL'sini al
                    secure_api = "https://securevideotoken.tmgrup.com.tr/webtv/secure"
                    token_res = requests.get(
                        secure_api,
                        params={"url": raw_hls_url},
                        headers=headers,
                        verify=False
                    )

                    if token_res.status_code == 200:
                        token_data = token_res.json()
                        if token_data.get("Success"):
                            secure_hls_url = token_data.get("Url")

                            # 3. Aşama: Güvenli m3u8 içeriğini çek ve görece bağlantıları tam URL'ye dönüştür
                            m3u8_res = requests.get(secure_hls_url, headers=headers, verify=False)
                            if m3u8_res.status_code == 200:
                                base_url = secure_hls_url.rsplit('/', 1)[0] + '/'
                                modified_content = ""

                                for line in m3u8_res.text.splitlines():
                                    line_str = line.strip()
                                    if line_str and not line_str.startswith("#"):
                                        if not line_str.startswith("http"):
                                            modified_content += base_url + line_str + "\n"
                                        else:
                                            modified_content += line_str + "\n"
                                    else:
                                        modified_content += line + "\n"

                                print(modified_content)
                            else:
                                print("Error fetching m3u8 content.")
                        else:
                            print("Secure token request was not successful.")
                    else:
                        print("Error fetching secure token URL.")
                else:
                    print("Video API success status is False.")
            except Exception as e:
                print(f"JSON parsing error: {e}")
        else:
            print("Error fetching video metadata.")
    else:
        print("data-videoid or data-websiteid not found in page content.")
else:
    print(f"Error: Status code {response.status_code}")
