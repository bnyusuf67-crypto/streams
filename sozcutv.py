import os
import requests

playlist_url = "https://raw.githubusercontent.com/k33n26/vavoo/refs/heads/main/iptv.m3u"
output_file = "streams/sozcutv.m3u8"

# Playlist'i indir
response = requests.get(playlist_url)
response.raise_for_status()

lines = response.text.splitlines()

stream_url = None

# Tırnak çakışmasını önlemek için dış tırnak tek tırnak
target_line = '#EXTINF:-1 tvg-id="SozcuTV.tr@SD" tvg-name="SZC .c" tvg-logo="https://logo.huhu.to/logo?c=2036794972.png" group-title="Haber",SZC .c'

for i, line in enumerate(lines):
    if line.strip() == target_line:
        if i + 1 < len(lines):
            stream_url = lines[i + 1].strip()
        break

if not stream_url:
    raise Exception("SZC TV not found in playlist")

# Klasör yoksa oluştur
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Satırları temiz ve kesin bir formatta oluştur
m3u8_lines = [
    "#EXTM3U",
    "#EXT-X-STREAM-INF:BANDWIDTH=7680000",
    stream_url
]

# Satır sonlarını tam olarak \n ile birleştirip kaydet
with open(output_file, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(m3u8_lines) + "\n")

print(f"Saved to {output_file}")
