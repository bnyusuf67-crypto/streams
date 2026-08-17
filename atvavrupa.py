import os
import requests

playlist_url = "https://raw.githubusercontent.com/bnyusuf67-crypto/Get-website-information/refs/heads/main/playlist.m3u"
output_file = "streams/atvavrupa.m3u8"

# Download playlist
response = requests.get(playlist_url)
response.raise_for_status()

lines = response.text.splitlines()

stream_url = None

for i, line in enumerate(lines):
    if line.strip() == "#EXTVLCOPT:http-referrer=https://www.atvavrupa.tv/canli-yayin":
        if i + 1 < len(lines):
            stream_url = lines[i + 1].strip()
        break

if not stream_url:
    raise Exception("ATV Avrupa not found in playlist")

# Download the referenced m3u8
stream_response = requests.get(stream_url)
stream_response.raise_for_status()

os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    f.write(stream_response.text)

print(f"Saved to {output_file}")
