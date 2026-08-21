import os
import requests

playlist_url = "https://raw.githubusercontent.com/k33n26/vavoo/refs/heads/main/iptv.m3u"
output_file = "streams/sozcutv.m3u8"

response = requests.get(playlist_url)
response.raise_for_status()

# Gelen veriyi \r\n veya \n fark etmeksizin temiz parçalara böl
lines = [line.strip() for line in response.text.splitlines() if line.strip()]

stream_url = None
target_line = '#EXTINF:-1 tvg-id="SozcuTV.tr@SD" tvg-name="SZC .c" tvg-logo="https://logo.huhu.to/logo?c=2036794972.png" group-title="Haber",SZC .c'

for i, line in enumerate(lines):
    if line == target_line:
        if i + 1 < len(lines):
            stream_url = lines[i + 1]
        break

if not stream_url:
    raise Exception("SZC TV not found in playlist")

os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Formatı f-string veya üçlü tırnak kullanmadan doğrudan yazma
with open(output_file, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    f.write("#EXT-X-STREAM-INF:BANDWIDTH=7680000\n")
    f.write(f"{stream_url}\n")

print(f"Saved to {output_file}")
