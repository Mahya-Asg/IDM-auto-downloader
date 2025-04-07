import requests # Library to fetch web page content
from bs4 import BeautifulSoup # Library to parse HTML
import urllib.parse # Library to join relative URLs with the base URL
import subprocess # Library to run external programs like IDM
import os # Library to check if the IDM path exists

# --- Configuration ---
# remember to use Iran IP for this link 
SERVER_URL = "https://dls5.iran-gamecenter-host.com/DonyayeSerial/series2/tt11126994/SoftSub/S02/720p.x265.10bit.Web-DL/"

IDM_PATH = r"C:\Program Files (x86)\Internet Download Manager\IDMan.exe"
# Using r"..." (raw string) helps handle backslashes in Windows paths correctly.

# --- Check if IDM Executable Exists ---
if not os.path.exists(IDM_PATH):
    print(f"Error: IDM executable not found at path: {IDM_PATH}")
    print("Please update the IDM_PATH variable in the script.")
    exit() # Stop the script if IDM isn't found

# --- Step 1: Fetch the Web Page Content ---
print(f"Fetching page content from: {SERVER_URL}")
try:
    response = requests.get(SERVER_URL, timeout=30) # Timeout after 30 seconds
    response.raise_for_status() # Raise an exception for bad status codes (like 404, 500)
    html_content = response.text
    print("Successfully fetched page content.")
except requests.exceptions.RequestException as e:
    print(f"Error fetching URL {SERVER_URL}: {e}")
    exit() # Stop the script if the page can't be fetched

# --- Step 2: Parse the HTML ---
print("Parsing HTML content...")
soup = BeautifulSoup(html_content, 'html.parser')

# --- Step 3: Find MKV Links and Construct Full URLs ---
mkv_links = []
print("Searching for MKV links...")
# Find all anchor tags (<a>) in the parsed HTML
for link in soup.find_all('a'):
    href = link.get('href') # Get the value of the 'href' attribute
    if href and href.lower().endswith('.mkv'):
        # Check if the link ends with .mkv (case-insensitive)
        # Construct the absolute URL by joining the base server URL and the found href
        # This handles both absolute (http://...) and relative (movie.mkv) links correctly
        full_url = urllib.parse.urljoin(SERVER_URL, href)
        mkv_links.append(full_url)
        print(f"  Found MKV link: {full_url}")

# Check if any links were found
if not mkv_links:
    print("No .mkv links found on the page.")
    exit()

print(f"\nFound {len(mkv_links)} MKV file(s).")

# --- Step 4: Call IDM for Each Link ---
print("Adding links to Internet Download Manager...")
for index, url in enumerate(mkv_links):
    print(f"  Adding ({index + 1}/{len(mkv_links)}): {url}")
    try:
        # Construct the command arguments for IDM
        # IDMan.exe /d URL [/p path] [/f filename] [/q] [/h] [/n] [/a]
        # /d <URL> - Instructs IDM to download the specified URL
        # /n - Silent mode: Don't ask any questions (like download confirmation)
        # /a - Add the file to the download queue, but don't start downloading automatically (optional)
        # We will use /d and /n here. Remove /a if you want downloads to start immediately.
        command = [
            IDM_PATH,   # Path to IDM executable
            "/d",       # Command to download
            url,        # The URL to download
            "/n"        # Silent mode
            # "/a"      # Optional: Add to queue without starting
        ]

        # Execute the command
        # Using subprocess.run is generally preferred for running a command and waiting
        # capture_output=True helps see if IDM prints errors, text=True decodes them
        result = subprocess.run(command, capture_output=True, text=True, check=False) # check=False prevents raising error if IDM returns non-zero exit code

        # Optional: Check IDM's output/errors (might not always be informative)
        if result.returncode != 0:
            print(f"    Warning: IDM process returned non-zero exit code ({result.returncode}) for {url}.")
            if result.stderr:
                 print(f"    IDM stderr: {result.stderr.strip()}")
        else: 
           print(f"    Successfully sent '{url}' to IDM.")

    except Exception as e:
        print(f"  Error adding link {url} to IDM: {e}")

print("\nScript finished. Check IDM to see the added downloads.")