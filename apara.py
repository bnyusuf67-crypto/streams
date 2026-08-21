import os
import re
import requests

playlist_url = "https://raw.githubusercontent.com/k33n26/vavoo/refs/heads/main/iptv.m3u"
output_file = "streams/apara.m3u8"

response = requests.get(playlist_url)
response.raise_for_status()

# Gelen tüm metindeki görünmeyen kontrol karakterlerini (\r, \0 vb.) baştan sil
raw_text = re.sub(r'[\r\x00-\x08\x0b\x0c\x0e-\x1f]', '', response.text)
lines = raw_text.splitlines()

stream_url = None

# Birebir satır eşleşmesi yerine kanal adını veya ID'sini esnek arayalım
for i, line in enumerate(lines):
    if '#EXTINF' in line and ('APARA HD .b' in line):
        if i + 1 < len(lines):
            # Alt satırdaki URL'yi al ve sadece alfabetik/sayısal/link karakterlerini koru
            candidate = lines[i + 1].strip()
            if candidate.startswith("http"):
                stream_url = candidate
                break

if not stream_url:
    raise Exception("A News not found in playlist")

os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Dosyaya byte (binary) modunda yazarak sistemin karakter eklemesini engelle
output_content = f"#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=7680000\n{stream_url}\n"

with open(output_file, "wb") as f:
    f.write(output_content.encode("utf-8"))

print(f"Saved to {output_file}")
