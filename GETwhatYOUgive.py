import os
from datetime import datetime, timedelta
import requests

# Configuration
BASE_URL = "https://client.lahii.com/stat"

# Output directory for downloaded CSVs
OUTPUT_DIR = "downloaded_logs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define date range: Last 1 year (365 days back from today)
end_date = datetime.now().date()
start_date = end_date - timedelta(days=365)

# Use a Session to maintain cookies/state automatically
session = requests.Session()

# Headers matching your browser's request
headers = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101"
        " Firefox/153.0"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://client.lahii.com",
    "Referer": "https://client.lahii.com/stat",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}
session.headers.update(headers)

print("[*] Initializing session by visiting the stats page...")
try:
  # First, perform a GET request to the page to load any session cookies or tokens
  init_response = session.get(BASE_URL, timeout=30)
  print(f"[*] Initial connection status: {init_response.status_code}")
  print(f"[*] Active session cookies: {session.cookies.get_dict()}")
except Exception as e:
  print(f"[!] Error connecting to server: {e}")
  exit(1)

# Loop day by day (single-day exports to respect server limits)
current_date = start_date
while current_date <= end_date:
  day_str = current_date.strftime("%Y-%m-%d")
  print(f"[-] Downloading logs for {day_str}...")

  # Form data payload for the POST request
  payload = {"start_time": day_str, "end_time": day_str}

  try:
    # Send POST request using the session
    response = session.post(BASE_URL, data=payload, timeout=30)

    content_type = response.headers.get("content-type", "")

    # Check if the server returned a CSV file
    if response.status_code == 200 and "text/csv" in content_type:
      filename = os.path.join(OUTPUT_DIR, f"event_log_{day_str}.csv")
      with open(filename, "wb") as f:
        f.write(response.content)
      print(f"[+] Saved: {filename}")
    else:
      print(
          f"[!] Failed for {day_str}. Server returned content-type:"
          f" {content_type}"
      )
      # If it returns HTML, it likely means authentication failed or session expired
      if "text/html" in content_type:
        print(
            "[!] Received HTML instead of CSV. Your session may require manual"
            " login cookies."
        )

  except Exception as e:
    print(f"[!] Error downloading {day_str}: {e}")

  # Move to the next day
  current_date += timedelta(days=1)

print("\n[+] Batch download process completed!")
