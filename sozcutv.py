import os
import requests

playlist_url = "https://raw.githubusercontent.com/k33n26/vavoo/refs/heads/main/iptv.m3u"
output_file = "streams/sozcutv.m3u8"

# Download playlist
response = requests.get(playlist_url)
response.raise_for_status()

lines = response.text.splitlines()

stream_url = None

for i, line in enumerate(lines):
    if line.strip() == "#EXTINF:-1 tvg-id="SozcuTV.tr@SD" tvg-name="SZC .c" tvg-logo="https://logo.huhu.to/logo?c=2036794972.png" group-title="Haber",SZC .c":
        if i + 1 < len(lines):
            stream_url = lines[i + 1].strip()
        break

if not stream_url:
    raise Exception("SZC TV not found in playlist")

# Download the referenced m3u8
stream_response = requests.get(stream_url)
stream_response.raise_for_status()

os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    f.write(stream_response.text)

print(f"Saved to {output_file}")
