import os
import re
import subprocess
import urllib.request
import zipfile
import shutil
import sys
import pkg_resources
import feedparser

if os.geteuid() == 0:
    print("This script should not be run as root (i.e., with sudo). Please run the script as a non-root user.")
    exit()

package_list = [
    'alabaster==0.7.10',
    'Babel==2.8.0',
    'beautifulsoup4==4.11.1',
    'bs4==0.0.1',
    'certifi==2022.12.7',
    'chardet==3.0.4',
    'docutils==0.16',
    'feedparser==6.0.10',
    'google-alerts==0.2.9',
    'idna==3.4',
    'imagesize==1.0.0',
    'Jinja2==3.0.3',
    'MarkupSafe==2.1.1',
    'packaging==22.0',
    'pkginfo==1.4.2',
    'Pygments==2.13.0',
    'pyparsing==2.4.7',
    'pytz==2021.1',
    'requests==2.28.1',
    'requests-toolbelt==0.9.1',
    'selenium==4.0.0a1',
    'six==1.16.0',
    'snowballstemmer==1.2.1',
    'Sphinx==1.7.4',
    'sphinx-rtd-theme==0.3.0',
    'sphinxcontrib-websupport==1.0.1',
    'tqdm==4.64.1',
    'twine==1.11.0',
    'urllib3==1.26.13'
]

for package_name in package_list:
    try:
        pkg_resources.get_distribution(package_name)
    except pkg_resources.DistributionNotFound:
        print(f"Package {package_name} not found. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
    except pkg_resources.VersionConflict:
        print(f"Version conflict for package {package_name}. Uninstalling existing version and installing required version...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', package_name])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])

print("All required packages have been installed.")    
packages_installed = "Packages Installed: True"
    
# Check if Chromium is installed
if shutil.which("chromium") is None:
    print("Chromium is not installed. Installing Chromium...")
    try:
        # Install Chromium using apt-get command
        subprocess.check_call(['sudo', 'apt-get', 'update'])
        subprocess.check_call(['sudo', 'apt-get', 'install', 'chromium', '-y'])
        print("Chromium installed successfully!")
        chromium_install = "Chromium Installed: True"
    except subprocess.CalledProcessError as e:
        print("Error installing Chromium:", e)
        chromium_install = "Chromium Not Installed"
        exit()

# Get the current version of Chromium
output = os.popen('chromium --product-version').read().strip()
print(f"Current Chromium version is {output}")
chromium_install = "Chromium Installed: True"

# Define the versions and corresponding ChromeDriver URLs
versions = {
    "111": "https://chromedriver.storage.googleapis.com/111.0.5563.41/chromedriver_linux64.zip",
    "110": "https://chromedriver.storage.googleapis.com/110.0.5481.77/chromedriver_linux64.zip",
    "109": "https://chromedriver.storage.googleapis.com/109.0.5414.74/chromedriver_linux64.zip",
}

# Check if the current version matches any of the versions in the dictionary
if output.startswith("110"):
    version_number = "110"
elif output.startswith("109"):
    version_number = "109"
elif output.startswith("111"):
    version_number = "111"
else:
    print("No matching ChromeDriver version found")
    exit()

# Check if /tmp/chromedriver already exists and remove it if it does
if os.path.exists("/tmp/chromedriver"):
    shutil.rmtree("/tmp/chromedriver")

# Create the /tmp/chromedriver directory
os.makedirs("/tmp/chromedriver")

# Check if the zip file already exists and remove it if it does
filename = f"chromedriver_{version_number}.zip"
if os.path.exists(filename):
    os.remove(filename)

# Download the corresponding ChromeDriver zip file
url = versions[version_number]
urllib.request.urlretrieve(url, filename)

# Extract the contents of the zip file to /tmp/
with zipfile.ZipFile(filename, "r") as zip_ref:
    zip_ref.extractall("/tmp/chromedriver")

# Remove the zip file
os.remove(filename)

chromedriver_path = '/tmp/chromedriver/chromedriver'

# Set executable permission for owner, group, and others
os.chmod(chromedriver_path, 0o755)
print(f"Downloaded and extracted ChromeDriver for version {version_number}")

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
        
# Check if /tmp/chromedriver exists
if os.path.exists('/tmp/chromedriver'):
    chromedriver='Chromedriver Installed: True'
else:
    chromedriver='/tmp/chromedriver does not exist'

def enter_credentials():
    if os.geteuid() == 0:
        print("Please do not run this script as sudo.")
        return
    try:
        email = input("Enter your email: ")
        password = input("Enter your password: ")
        subprocess.run(['google-alerts', 'setup', '--email', email, '--password', password])
        clear_screen()
    except subprocess.CalledProcessError:
        print("Invalid credentials. Please try again.")
        input("Press Enter to continue...")
        enter_credentials()

def seed_database():
    subprocess.run(['google-alerts', 'seed', '--driver', '/tmp/chromedriver/chromedriver', '--timeout', '60'])


def monitor_word():
    word = input("Enter the word you want to monitor: ")
    subprocess.run(['google-alerts', 'create', '--term', word, '--delivery', 'rss', '--frequency', 'realtime'])
    clear_screen()

def delete_monitored_word():
    print("In development")
    input("Press Enter to continue...")

def request_feed():
    # Remove the file if it already exists
    if os.path.exists("feed.txt"):
        os.remove("feed.txt")

    # Open the file in append mode
    with open("feed.txt", "a") as f:
        # Run the google-alerts list command and capture its output
        result = subprocess.run(["google-alerts", "list"], capture_output=True, text=True)

        # Extract the RSS links from the output using regular expressions
        rss_links = re.findall(r"rss_link\": \"(.*?)\"", result.stdout)

        # Process each RSS link
        for url in rss_links:
            feed = feedparser.parse(url)

            for entry in feed.entries:
                title = entry.title.replace("<b>", "").replace("</b>", "")
                summary = entry.summary.replace("<b>", "").replace("</b>", "").replace("&nbsp;", " ")
                link = re.search(r"url=(.*?)&ct", entry.link).group(1)

                # Write the feed content to the file
                f.write(f"{title}\n")
                f.write(f"{link}\n")
                f.write(f"{summary}\n\n")

def display_feed():
    # Remove the file if it already exists
    if os.path.exists("feed_dates.txt"):
        os.remove("feed_dates.txt")

    # Open the file in append mode
    with open("feed_dates.txt", "a") as f:
        # Run the google-alerts list command and capture its output
        result = subprocess.run(["google-alerts", "list"], capture_output=True, text=True)

        # Extract the RSS links from the output using regular expressions
        rss_links = re.findall(r"rss_link\": \"(.*?)\"", result.stdout)

        # Process each RSS link and display feed content
        for url in rss_links:
            feed = feedparser.parse(url)

            for entry in feed.entries:
                title = entry.title.replace("<b>", "").replace("</b>", "")
                summary = entry.summary.replace("<b>", "").replace("</b>", "").replace("&nbsp;", " ")
                link = re.search(r"url=(.*?)&ct", entry.link).group(1)
                published = entry.published
                updated = entry.updated

                # Write the feed content to the file
                f.write(f"{title}\n")
                f.write(f"{link}\n")
                f.write(f"{summary}\n")
                f.write(f"{published}\n")
                f.write(f"{updated}\n\n\n")

def add_words():
    filename = input("Enter the name of the input file (type 'back' to go back to menu): ")
    if filename == 'back':
        return

    # Check if the file exists
    if not os.path.isfile(filename):
        print(f"Invalid file name: {filename}")
        return

    # Open the input file in read-only mode
    with open(filename, 'r') as input_file:
        # Loop through each line (word) in the input file
        for line in input_file:
            # Strip any whitespace from the line
            word = line.strip()

            # Print the word that is being added
            print(f"{word} (added)")
            
            # Create the Google Alert command with the current word
            command = f'google-alerts create --term "{word}" --delivery \'rss\' --frequency \'realtime\' >/dev/null 2>&1'
            
            # Run the command using os.system() and redirect output to /dev/null
            os.system(command)

    # Return to the menu
    return

def bestorallresults():
    # Prompt the user for email and password
    email = input("Enter your email: ")
    password = input("Enter your password: ")

    # Create an instance
    ga = GoogleAlerts(email, password)

    # Authenticate your user
    ga.authenticate()

    # Show delivery options to the user
    print("Please select a delivery option:")
    print("1: BEST Results")
    print("2: ALL Results")

    # Prompt the user for a valid option
    while True:
        option = input("Enter 1 or 2: ")
        if option in ["1", "2"]:
            break
        else:
            print("Invalid option. Please enter 1 or 2.")

    # Set delivery option based on user's selection
    delivery_option = "BEST" if option == "1" else "ALL"

    # List configured monitors
    monitors = ga.list()

    # Modify all monitors
    for monitor in monitors:
        if "monitor_id" in monitor:
            monitor_id = monitor["monitor_id"]
            ga.modify(monitor_id, {'delivery': 'RSS', 'monitor_match': delivery_option})

# Define a function to print a line separator
def print_separator():
    print("=" * 50)
word_count = 0
while True:
    if os.path.exists('feed.txt'):
        feedexists = "Feed.txt Exists: True"
    else:
        feedexists = "Feed.txt Exists: \033[91mFalse\033[0m"
    clear_screen()
    config_exists = os.path.exists(os.path.expanduser('~/.config/google_alerts/config.json'))
    session_exists = os.path.exists(os.path.expanduser('~/.config/google_alerts/session'))
    discordtoken_exists = os.path.exists(os.path.expanduser('~/.config/google_alerts/discordtoken'))
    # Print the installation and database status
    print(f"{'Installation Status':^50}")
    print_separator()
    if config_exists:
        print("User Credentials Supplied:", config_exists)
    else:
        print("User Credentials Supplied: \033[91mFalse\033[0m")
    if session_exists:
        print("Database Seeded:", session_exists)
    else:
        print("Database Seeded: \033[91mFalse\033[0m")
    print(f"{chromedriver}")
    print(f"{chromium_install}")
    print(f"{packages_installed}")
    print(f"{feedexists}")
    if session_exists:
        print("Discord Token Added:", discordtoken_exists)
    else:
        print("Discord Token Added: \033[91mFalse\033[0m")

    print_separator()
    
    # Print the menu options
    print(f"{'Menu':^50}")
    print_separator()
    print("(1) Enter new credentials")
    print("(2) Seed the database")
    if not config_exists or not session_exists:
        print("(3) Monitor a word (Please login and seed first)")
        print("(4) Delete a monitored word (Please login and seed first)")
        print("(5) List all words being monitored (Please login and seed first)")
        print("(6) Request feed (Please login and seed first)")
        print("(7) Request feed with formatting (Please login and seed first)")
        print("(8) Add words from file (Please login and seed first)")
        print("(9) Change to Best or All results (Please login and seed first)")
    else:
        print("(3) Monitor a word")
        print("(4) Delete a monitored word")
        if word_count > 0:
            print(f"(5) List all words being monitored ({word_count})")
        else:
            print("(5) List all words being monitored")
        print("(6) Request feed")
        print("(7) Request feed with formatting")
        print("(8) Add words from file")
        print("(9) Change to Best or All results")
        print("(10) Add Discord Token")
        print("(11) Run Discord Bot")
    print("(exit) Exit")
    print_separator()
    choice = input("Enter your choice: ")
    if choice == '1':
        enter_credentials()
    elif choice == '2':
        captcha_choice = input("Choose an option:\n1. No captcha\n2. Has captcha\n")
        if captcha_choice == '1':
            seed_database()
        elif captcha_choice == '2':
            # Replace the arguments below with the appropriate values for your system
            os.system("python3 captchaproblem.py seed --driver /tmp/chromedriver/chromedriver --timeout 60")
        else:
            print("Invalid choice. Please choose again.")
    elif choice == '3' and (not config_exists or not session_exists):
        print("Please login and seed the database first.")
        input("Press Enter to continue...")
    elif choice == '4' and (not config_exists or not session_exists):
        print("Please login and seed the database first.")
        input("Press Enter to continue...")
    elif choice == "5" and (not config_exists or not session_exists):
        print("Please login and seed the database first.")
        input("Press Enter to continue...")
    elif choice == '3':
        monitor_word()
    elif choice == '4':
        delete_monitored_word()
    elif choice == "5":
        output = subprocess.check_output(['google-alerts', 'list']).decode('utf-8')
        monitored_words = re.findall(r'"term": "(.+)",', output)
        if len(monitored_words) == 0:
            print("No monitored words found.")
            input("Press Enter to continue...")
        else:
            for word in monitored_words:
                word_count += len(word.split())
                print(word)
            print(f"Total word count: {word_count}")
            input("Press Enter to continue...")
    elif choice == '6' and (not config_exists or not session_exists):
        print("Please login and seed first.")
        input("Press Enter to continue...")
    elif choice == '6':
        print("Writing to feed.txt, this could take some time...")
        request_feed()
    elif choice == '7' and (not config_exists or not session_exists):
        print("Please login and seed first.")
        input("Press Enter to continue...")
    elif choice == '7':
        print("Writing to feed_dates.txt...")
        display_feed()
    elif choice == '8' and (not config_exists or not session_exists):
        print("Please login and seed first.")
        input("Press Enter to continue...")
    elif choice == '8':
        word_choice = input("Choose an option:\n1. From a wordlist\n2. Individual word\n")
        if word_choice == '1':
            add_words()
        elif word_choice == '2':
            monitor_word()
        else:
            print("Invalid choice. Please choose again.")
    elif choice == '9' and (not config_exists or not session_exists):
        print("Please login and seed first.")
        input("Press Enter to continue...")
    elif choice == '9':
        bestorallresults()
    elif choice == "10":
        discord_token = input("Enter Discord token: ")
        config_dir = os.path.expanduser("~/.config/google_alerts")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        with open(os.path.join(config_dir, "discordtoken"), "w") as f:
            f.write(discord_token)
            print("Discord token saved successfully.")
    elif choice == '11':
            if os.path.exists('feed.txt'):
                feedexists = "Feed.txt Exists: True"
                os.system('python3 bot.py')
            else:
                print("Please generate the feed first")
            feedexists = "Feed.txt Exists: \033[91mFalse\033[0m"
    elif choice == 'exit':
        break
    else:
        print("Invalid choice.")
        input("Press Enter to continue...")
