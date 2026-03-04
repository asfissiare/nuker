import threading
import json
import time
import requests
import os
from colorama import Fore
import queue
from pystyle import *
import discord 
import asyncio
indexed_channels = [] 


# VARIABLES 
msg = 0
chd = 0
chm = 0
err = 0
banned = []
tkn = None
session = requests.Session()

# ID SCRAPING AVANZATO
import requests
import os

# GRADIENT
def gradient_text(text, index, total):
    start = (0, 255, 0)   # verde
    end   = (255, 255, 255)  # bianco

    ratio = index / max(total - 1, 1)
    r = int(start[0] + (end[0] - start[0]) * ratio)
    g = int(start[1] + (end[1] - start[1]) * ratio)
    b = int(start[2] + (end[2] - start[2]) * ratio)

    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


# ID SCRAPER AVANZATO
def scrape_members(guild_id, token, file_path='scraped/members.txt'):
    headers = {'Authorization': f"Bot {token}"}

    # RUOLI
    roles_url = f"https://discord.com/api/v10/guilds/{guild_id}/roles"
    roles_resp = requests.get(roles_url, headers=headers)
    if roles_resp.status_code != 200:
        print("Errore nel recupero dei ruoli.")
        return

    roles_data = roles_resp.json()
    role_map = {r["id"]: r["name"] for r in roles_data}

    # SCRAPING MEMBERS
    all_members = []
    after = None

    while True:
        url = f"https://discord.com/api/v10/guilds/{guild_id}/members?limit=1000"
        if after:
            url += f"&after={after}"

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            members = response.json()
            if not members:
                break
            all_members.extend(members)
            after = members[-1]['user']['id']
        else:
            print(f"Errore scraping membri: {response.status_code}")
            return


    os.makedirs(os.path.dirname(file_path), exist_ok=True)


    with open(file_path, 'w') as f:
        for m in all_members:
            f.write(m['user']['id'] + '\n')

 
    print("\n")
    print(gradient_text("╔══════════════════════════════════════════════════════╗", 0, 10))
    print(gradient_text("║              MEMBER SCRAPER COMPLETATO               ║", 2, 10))
    print(gradient_text("╠══════════════════════════════════════════════════════╣", 4, 10))
    print(gradient_text(f"║  ✓ Membri trovati: {len(all_members):<33} ║", 5, 10))
    print(gradient_text(f"║  ✓ Salvati in: {file_path:<34}       ║", 6, 10))
    print(gradient_text("╚══════════════════════════════════════════════════════╝", 9, 10))
  

    print(gradient_text(f"[ ✓ ] Membri trovati: {len(all_members)}", 2, 10))
    print(gradient_text(f"[ ✓ ] Salvati in: {file_path}", 4, 10))

   
    print("\n" + gradient_text("MEMEBERS AND ROLES", 5, 10))

    indexed_members = []  

    for idx, m in enumerate(all_members, start=1):
        uid = m['user']['id']
        uname = m['user'].get('username', 'Unknown')

        role_ids = m.get('roles', [])
        role_names = [role_map.get(rid, f"Unknown({rid})") for rid in role_ids]

        indexed_members.append(uid)

        line = f"[ {idx:03} ] {uname:<20} | Ruoli: {', '.join(role_names) if role_names else 'Nessun ruolo'}"
        print(gradient_text(line, idx % 10, 10))

    print("\n" + gradient_text("SKIP DM", 7, 10))
    print("Inserisci i numeri degli utenti da saltare (es: 001, 002, 010)")
    raw = input("→ ").replace(" ", "")

    skip_list = []

    if raw:
        try:
            nums = raw.split(",")
            for n in nums:
                index = int(n)
                if 1 <= index <= len(indexed_members):
                    skip_list.append(indexed_members[index - 1])
        except:
            pass

    print(gradient_text(f"[ ✓ ] Salterai {len(skip_list)} utenti.", 9, 10))
    print("")

    return all_members, skip_list

# UTILITIES
def print_message(action, success=True, response_code=None):
    if success:
        status = f"{Fore.GREEN}[ ~ ]"
    else:
        status = f"{Fore.RED}[ ! ]"
    if response_code is not None:
        status += f" Response Code: {response_code}"
    print(f"{status}     {action}")


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def set_console_title(title):
    os.system(f"title {title}")


def get_integer_input(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print_message("Please enter a valid integer.", success=False)


def get_valid_token():
    while True:
        tkn = input(f"[ + ]     Token: ")
        headers = {'Authorization': f"Bot {tkn}"}
        Write.Print(f"[ + ]     Checking token.\n", Colors.green, interval=.005)
        response = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
        if response.status_code == 200:
            Write.Print(f"[ + ]     Token valid.\n", Colors.green, interval=.005)
            return tkn
        else:
            Write.Print(f"[ + ]     Please enter a valid token.\n", Colors.green, interval=.005)


def is_valid_guild_id(guild_id):
    headers = {'Authorization': f"Bot {tkn}"}
    response = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}", headers=headers)
    return response.status_code == 200


# SERVERS LIST
def select_guilds(token):
    headers = {"Authorization": f"Bot {token}"}

    Write.Print("[ + ]     Fetching guilds...\n", Colors.green, interval=.005)
    response = requests.get("https://discord.com/api/v10/users/@me/guilds", headers=headers)

    if response.status_code != 200:
        print_message("Impossibile recuperare i server del bot.", success=False)
        return []

    guilds = response.json()
    if not guilds:
        print_message("Il bot non è in nessun server.", success=False)
        return []

    print("\n")
    print("╔══════════════════════════════════════════════════════╗")
    print("║                   SERVER DISPONIBILI                 ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    indexed = []

    for idx, g in enumerate(guilds, start=1):
        name = g["name"]
        gid = g["id"]
        indexed.append(gid)

        line = f"[ {idx:03} ]  {name} (ID: {gid})"
        print(line)

    print("")
    raw = input("[ + ]     Seleziona i server (es: 1, 3, 5): ").replace(" ", "")
    selected = []

    if raw:
        try:
            nums = raw.split(",")
            for n in nums:
                i = int(n)
                if 1 <= i <= len(indexed):
                    selected.append(indexed[i - 1])
        except:
            print_message("Input non valido.", success=False)
            return []

    Write.Print(f"[ + ]     Server selezionati: {len(selected)}\n", Colors.green, interval=.005)
    return selected

# MSG SPAM
def spam():
    global tkn, svr

    # CHANNELS SCRAPING  
    headers = {'Authorization': f"Bot {tkn}"}
    response = requests.get(f"https://discord.com/api/v9/guilds/{svr}/channels", headers=headers)

    if response.status_code != 200:
        print_message("Errore nello scraping dei canali.", success=False)
        menu()
        return

    channels = response.json()

    print(f"\n{Fore.GREEN}[ + ]     Canali trovati: {len(channels)}{Fore.RESET}\n")

    indexed_channels = []
    for i, ch in enumerate(channels, start=1):
        print(f"{Fore.GREEN}[ {i} ]{Fore.RESET}  {ch.get('name', 'unknown')}  ({ch['id']})")
        indexed_channels.append(ch['id'])

    print("\n")
    print(f"{Fore.GREEN}[ 0 ]{Fore.RESET}  Spamma TUTTI i canali\n")

    while True:
        try:
            choice = int(input(f"{Fore.GREEN}[ + ]     Seleziona un canale (0 per tutti): {Fore.RESET}"))
            if 0 <= choice <= len(indexed_channels):
                break
        except:
            pass
        print_message("Scelta non valida.", success=False)

    msg_choice = input(f"{Fore.GREEN}[ + ]     Messaggio manuale (1) o file (2)? {Fore.RESET}")

    if msg_choice == "1":
        message = input(f"{Fore.GREEN}[ + ]     Messaggio: {Fore.RESET}")
    else:
        file_path = input(f"{Fore.GREEN}[ + ]     Percorso file: {Fore.RESET}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                message = f.read().strip()
        except:
            print_message("File non trovato.", success=False)
            message = input(f"{Fore.GREEN}[ + ]     Messaggio: {Fore.RESET}")

    amount = get_integer_input(f"{Fore.GREEN}[ + ]     Numero di messaggi: {Fore.RESET}")

    if choice == 0:
        threads = []
        for ch_id in indexed_channels:
            thread = threading.Thread(target=send_message_to_channel, args=(tkn, ch_id, message, amount))
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()
    else:
        selected_channel = indexed_channels[choice - 1]
        send_message_to_channel(tkn, selected_channel, message, amount)

    input(f"{Fore.GREEN}[ + ]     Completato. Premi invio per tornare al menu.{Fore.RESET}")
    menu()

indexed_channels = []
def send_message_to_channel(bottoken, channel_id, message, amount):
    url = f"https://discord.com/api/channels/{channel_id}/messages"
    headers = {'Authorization': f"Bot {bottoken}", 'Content-Type': 'application/json'}

    for _ in range(amount):
        data = {'content': message}
        requests.post(url, headers=headers, json=data)

def send_messages_to_all_channels(bottoken, guild_id, message, amount, num_threads=5):
    headers = {'Authorization': f"Bot {bottoken}"}
    response = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers=headers)
    channels = response.json()

    global indexed_channels
    indexed_channels = [channel["id"] for channel in channels]

    threads = []
    for channel in channels:
        channel_id = channel['id']
        thread = threading.Thread(target=send_message_to_channel, args=(bottoken, channel_id, message, amount))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()


def load_channels(bottoken, guild_id):
    global indexed_channels
    headers = {'Authorization': f"Bot {bottoken}"}
    response = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers=headers)
    channels = response.json()
    indexed_channels = [channel["id"] for channel in channels]

def tgspam():
    global tkn, svr, indexed_channels
    # TG ACC LINK
    message = "https://t.me/bruisesalloverme"

    amount = get_integer_input(f"{Fore.GREEN}[ + ]     Numero di messaggi per canale: {Fore.RESET}")

    if not indexed_channels:
        print(f"{Fore.YELLOW}[ ! ] Carico i canali del server...{Fore.RESET}")
        load_channels(tkn, svr)

    if not indexed_channels:
        print(f"{Fore.RED}[ ! ] Nessun canale trovato.{Fore.RESET}")
        input("Premi invio per tornare al menu...")
        return menu()

    threads = []
    for ch_id in indexed_channels:
        thread = threading.Thread(
            target=send_message_to_channel,
            args=(tkn, ch_id, message, amount)
        )
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    input(f"{Fore.GREEN}[ + ]     Completato. Premi invio per tornare al menu.{Fore.RESET}")
    menu()

    # CHANNELS SCRAPING  
    headers = {'Authorization': f"Bot {tkn}"}
    response = requests.get(f"https://discord.com/api/v9/guilds/{svr}/channels", headers=headers)

    if response.status_code != 200:
        print_message("Errore nello scraping dei canali.", success=False)
        menu()
        return

    channels = response.json()

    # CHANNEL LIST
    print(f"\n{Fore.GREEN}[ + ]     Canali trovati: {len(channels)}{Fore.RESET}\n")

    indexed_channels = []
    for i, ch in enumerate(channels, start=1):
        print(f"{Fore.GREEN}[ {i} ]{Fore.RESET}  {ch.get('name', 'unknown')}  ({ch['id']})")
        indexed_channels.append(ch['id'])

    print("\n")
    print(f"{Fore.GREEN}[ 0 ]{Fore.RESET}  Spamma TUTTI i canali\n")

    # CHANNEL CHOICHE
    while True:
        try:
            choice = int(input(f"{Fore.GREEN}[ + ]     Seleziona un canale (0 per tutti): {Fore.RESET}"))
            if 0 <= choice <= len(indexed_channels):
                break
        except:
            pass
        print_message("Scelta non valida.", success=False)

    # MESSAGE
    msg_choice = input(f"{Fore.GREEN}[ + ]     Messaggio manuale (1) o file (2)? {Fore.RESET}")

    if msg_choice == "1":
        message = input(f"{Fore.GREEN}[ + ]     Messaggio: {Fore.RESET}")
    else:
        file_path = input(f"{Fore.GREEN}[ + ]     Percorso file: {Fore.RESET}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                message = f.read().strip()
        except:
            print_message("File non trovato.", success=False)
            message = input(f"{Fore.GREEN}[ + ]     Messaggio: {Fore.RESET}")

    amount = get_integer_input(f"{Fore.GREEN}[ + ]     Numero di messaggi: {Fore.RESET}")

    # SPAM 
    if choice == 0:
        # spam all channels
        threads = []
        for ch_id in indexed_channels:
            thread = threading.Thread(target=send_message_to_channel, args=(tkn, ch_id, message, amount))
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()
    else:
        # spam single channel
        selected_channel = indexed_channels[choice - 1]
        send_message_to_channel(tkn, selected_channel, message, amount)

    input(f"{Fore.GREEN}[ + ]     Completato. Premi invio per tornare al menu.{Fore.RESET}")
    menu()

# TG SPAM
def tgspam():
    global tkn, svr, indexed_channels

    # MESSAGE
    message = "https://t.me/bruisesalloverme"

    amount = get_integer_input(f"{Fore.GREEN}[ + ]     Numero di messaggi per canale: {Fore.RESET}")


    if not indexed_channels:
        print(f"{Fore.YELLOW}[ ! ] Carico i canali del server...{Fore.RESET}")
        load_channels(tkn, svr)

    threads = []
    for ch_id in indexed_channels:
        thread = threading.Thread(
            target=send_message_to_channel,
            args=(tkn, ch_id, message, amount)
        )
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    input(f"{Fore.GREEN}[ + ]     Completato. Premi invio per tornare al menu.{Fore.RESET}")
    menu()

# CHANNEL MANAGEMENT
def delete_channel(channel_id, token, result_queue, max_retries=5):
    headers = {'Authorization': f"Bot {token}"}
    for _ in range(max_retries):
        response = requests.delete(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers)
        if response.status_code == 200:
            result_queue.put(f"Channel {channel_id} deleted successfully.")
            return
        else:
            result_queue.put(f"Error deleting channel {channel_id}: {response.status_code}")
    result_queue.put(f'Max retries reached for deleting channel {channel_id}.')



def delete_all_channels(token, guild_id, num_threads=100):
    headers = {'Authorization': f"Bot {token}"}
    response = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers=headers)
    channels = response.json()

    result_queue = queue.Queue()
    threads = []
    for channel in channels:
        channel_id = channel['id']
        thread = threading.Thread(target=delete_channel, args=(channel_id, token, result_queue))
        thread.start()
        threads.append(thread)
    for t in threads: t.join()
    while not result_queue.empty():
        print_message(result_queue.get())

def channeldelete():
    global tkn, svr
    delete_all_channels(tkn, svr)
    print_message('All channels deleted.')

def create_channel(guild_id, token, channel_name, result_queue):
    headers = {'Authorization': f"Bot {token}", 'Content-Type': 'application/json'}
    data = {'name': channel_name, 'type': 0}
    response = requests.post(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers=headers, json=data)
    if response.status_code == 201:
        print_message(f"Channel '{channel_name}' created successfully.")
    else:
        print_message(f"Error creating channel '{channel_name}': {response.status_code}")

def channelcreate():
    global tkn, svr
    channel_name = input(f"{Fore.GREEN}[ + ]     Enter the channel name: ")
    num_channels = get_integer_input(f"{Fore.GREEN}[ + ]     Enter the number of channels to create: ")
    result_queue = queue.Queue()
    threads = []
    for _ in range(num_channels):
        thread = threading.Thread(target=create_channel, args=(svr, tkn, channel_name, result_queue))
        thread.start()
        threads.append(thread)
    for t in threads: t.join()
    while not result_queue.empty():
        print(result_queue.get())

# DM USERS (patched api)
def dm_all_users(token, server, message, amount=1, file_path='scraped/members.txt'):
    headers = {'Authorization': f"Bot {token}", 'Content-Type': 'application/json'}
    with open(file_path,'r') as file:
        user_ids = [line.strip() for line in file]

    def send_dm(user_id):
        channel_create_payload = {'recipient_id': user_id}
        response = requests.post(f"https://discord.com/api/v9/users/@me/channels",
                                 headers=headers, json=channel_create_payload)
        if response.status_code == 200:
            channel_id = response.json()['id']
            for i in range(amount):
                message_payload = {'content': message}
                r = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages",
                                  headers=headers, json=message_payload)
                if r.status_code == 200:
                    print_message(f"Message {i+1}/{amount} sent to user {user_id} successfully.",
                                  True, r.status_code)
                elif r.status_code == 429:
                    retry_after = r.json().get("retry_after", 1)
                    print_message(f"Rate limited. Waiting {retry_after} seconds...",
                                  False, r.status_code)
                    time.sleep(retry_after)
                    continue
                else:
                    print_message(f"Error sending message to user {user_id}: {r.status_code}",
                                  False, r.status_code)
                time.sleep(1.5)
        else:
            print_message(f"Error creating DM channel with user {user_id}: {response.status_code}",
                          False, response.status_code)

    # closing function
    for user_id in user_ids:
        send_dm(user_id)

# MAIN MENU
def menu():
    global tkn, svr
    clear()
    print(Colorate.Vertical(Colors.green_to_white, Center.XCenter(ascii)))
    print(Colorate.Vertical(Colors.green_to_white, Center.XCenter(ascii2)))
    option = input(f"\n{Fore.GREEN}[ + ]     Option:  {Fore.RESET}")
    
    if option == "1":
        spam()
        input(f"{Fore.GREEN}[ + ]     Press enter to go back...")
        menu()
    elif option == "2":
        channelcreate()
        input(f"{Fore.GREEN}[ + ]     Press enter to go back...")
        menu()
    elif option == "3":
        channeldelete()
        input(f"{Fore.GREEN}[ + ]     Press enter to go back...")
        menu()
    elif option == "4":
        channeldelete()
        channelcreate()
        spam()
        input(f"{Fore.GREEN}[ + ]     Press enter to go back...")
        menu()

    elif option == "5":
        tgspam()
        input(f"{Fore.GREEN}[ + ]     Press enter to go back...")
        menu()
    elif option == "6":
        # AUTOMATIC ID SCRAPING FOR DM SPAM
        scrape_members(svr, tkn)

        choice = input(f"{Fore.GREEN}[ + ]     Vuoi scrivere il messaggio (1) o dare il percorso di un file (2)? {Fore.RESET}")
        if choice == "1":
            message = input(f"{Fore.RED}[ + ]     Message: ")
        else:
            file_path = input(f"{Fore.GREEN}[ + ]     Inserisci il percorso completo del file (es. C:\\Users\\franc\\Desktop\\Tools\\DS Nuker\\message.txt): {Fore.RESET}")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    message = f.read().strip()
            except FileNotFoundError:
                print_message("File non trovato, scrivi il messaggio manualmente.", success=False)
                message = input(f"{Fore.RED}[ + ]     Message: ")

        amount = get_integer_input(f"{Fore.GREEN}[ + ]     How many messages per user: {Fore.RESET}")
        dm_all_users(tkn, svr, message, amount)
        input(f"{Fore.GREEN}[ + ]     Press enter to go back...")
        menu()
    
    else:
        print(f"{Fore.RED} Invalid option. ")
        menu()
        
# BANNER
ascii = """
▄▄▌ ▐ ▄▌▄▄▄ .     ▄▄▄· ▄▄▌  ▄▄▌       ▄▄ •        ▐ ▄     ·▄▄▄▄  ▪  ▄▄▄ .
██· █▌▐█▀▄.▀·    ▐█ ▀█ ██•  ██•      ▐█ ▀ ▪▪     •█▌▐█    ██▪ ██ ██ ▀▄.▀·
██▪▐█▐▐▌▐▀▀▪▄    ▄█▀▀█ ██▪  ██▪      ▄█ ▀█▄ ▄█▀▄ ▐█▐▐▌    ▐█· ▐█▌▐█·▐▀▀▪▄
▐█▌██▐█▌▐█▄▄▌    ▐█ ▪▐▌▐█▌▐▌▐█▌▐▌    ▐█▄▪▐█▐█▌.▐▌██▐█▌    ██. ██ ▐█▌▐█▄▄▌
 ▀▀▀▀ ▀▪ ▀▀▀      ▀  ▀ .▀▀▀ .▀▀▀     ·▀▀▀▀  ▀█▄▀▪▀▀ █▪    ▀▀▀▀▀• ▀▀▀ ▀▀▀ 

                        t.me/bruisesalloverme"""                                  

ascii2 = """
╔════════════════════════════════╦════════════════════════════════╦════════════════════════════════╗
║ [ 1 ] - Spam all channels      ║ [ 2 ] - Create channels        ║ [ 3 ] - Delete channels        ║
╠════════════════════════════════╬════════════════════════════════╬════════════════════════════════╣
║ [ 4 ] - Full Nuke              ║[ 5 ] - TG Spam                 ║[ 6 ] - Mass Dm                 ║
╚════════════════════════════════╩════════════════════════════════╩════════════════════════════════╝"""

# START TOOL
clear()
set_console_title("Bruises")
print(Colorate.Vertical(Colors.green_to_white, Center.XCenter(ascii)))
tkn = get_valid_token()
selected = select_guilds(tkn)
if len(selected) == 1:
    svr = selected[0]
else:
    svr = selected
Write.Print("[ + ]     Guild valid.\n", Colors.green, interval=0.005)
clear()
menu()


