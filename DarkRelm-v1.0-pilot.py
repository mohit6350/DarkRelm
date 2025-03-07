#!/usr/bin/env python3
import os
import json
import getpass
import shutil
import subprocess
import urllib.request
from datetime import datetime
import urllib.parse

VAULT_FOLDER = "dark-relm-vault"
HISTORY_FILE = "darkrelm_history.json"
SESSION_FILES = []  # List to track all files created/downloaded during the session

def welcome_banner():
    banner = """
    =========================================
          Welcome to DarkRelm v2.4
    =========================================
    Enhanced secure vault with terminal!
    """
    print("\033[95m" + banner + "\033[0m")

def login():
    print("\033[93m--- Login ---\033[0m")
    username = input("Enter username: ")
    password = getpass.getpass("Set your vault password: ")
    print(f"\033[92mLogged in as {username}\033[0m")
    return username, password

def verify_vault_password(stored_password):
    attempt = getpass.getpass("\033[93mRe-enter your vault password: \033[0m")
    return attempt == stored_password

def save_history(action, username):
    history = load_history()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.append(f"{timestamp} - {username}: {action}")
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)
    if HISTORY_FILE not in SESSION_FILES:
        SESSION_FILES.append(HISTORY_FILE)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def initialize_vault():
    if not os.path.exists(VAULT_FOLDER):
        os.makedirs(VAULT_FOLDER)
        print(f"\033[92mVault '{VAULT_FOLDER}' created!\033[0m")
        if VAULT_FOLDER not in SESSION_FILES:
            SESSION_FILES.append(VAULT_FOLDER)

def simulate_downloads(username):
    for item in os.listdir():
        if item != VAULT_FOLDER and item != HISTORY_FILE and not item.endswith('.py'):
            src = item
            dst = os.path.join(VAULT_FOLDER, item)
            shutil.move(src, dst)
            save_history(f"Moved download '{item}' to vault", username)
            print(f"\033[92mMoved '{item}' to vault!\033[0m")
            if dst not in SESSION_FILES:
                SESSION_FILES.append(dst)

def create_file_in_vault(username, password):
    if verify_vault_password(password):
        file_name = input("\033[93mEnter file name (e.g., secret.txt): \033[0m")
        file_path = os.path.join(VAULT_FOLDER, file_name)
        content = input("Enter file content: ")
        with open(file_path, 'w') as f:
            f.write(content)
        save_history(f"Created file '{file_name}' in vault", username)
        print(f"\033[92mFile '{file_name}' created in vault!\033[0m")
        if file_path not in SESSION_FILES:
            SESSION_FILES.append(file_path)
    else:
        print("\033[91mIncorrect password, access denied!\033[0m")

def delete_item_in_vault(username, password):
    if verify_vault_password(password):
        item_name = input("\033[93mEnter file/folder name to delete: \033[0m")
        item_path = os.path.join(VAULT_FOLDER, item_name)
        if os.path.exists(item_path):
            if os.path.isfile(item_path):
                os.remove(item_path)
                save_history(f"Deleted file '{item_name}' from vault", username)
                print(f"\033[92mFile '{item_name}' deleted from vault!\033[0m")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                save_history(f"Deleted folder '{item_name}' from vault", username)
                print(f"\033[92mFolder '{item_name}' deleted from vault!\033[0m")
            if item_path in SESSION_FILES:
                SESSION_FILES.remove(item_path)
        else:
            print("\033[91mItem not found in vault!\033[0m")
    else:
        print("\033[91mIncorrect password, access denied!\033[0m")

def list_contents():
    print("\033[96m--- Current Directory Contents ---\033[0m")
    try:
        items = os.listdir()
        if not items:
            print("Directory is empty.")
        else:
            for item in items:
                item_path = os.path.join(os.getcwd(), item)
                item_type = "Folder" if os.path.isdir(item_path) else "File"
                print(f"{item_type}: {item}")
    except Exception as e:
        print(f"\033[91mError listing contents: {e}\033[0m")

def view_file(username, password):
    if verify_vault_password(password):
        file_name = input("\033[93mEnter file name to view: \033[0m")
        file_path = os.path.join(VAULT_FOLDER, file_name)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            print(f"\033[96m--- Contents of {file_name} ---\033[0m")
            print(content)
            save_history(f"Viewed file '{file_name}'", username)
        else:
            print("\033[91mFile not found!\033[0m")
    else:
        print("\033[91mIncorrect password, access denied!\033[0m")

def underworld_terminal_banner():
    banner = """
    =========================================
       Welcome to the UnderWorld!
    =========================================
    Navigate the shadows of your system!
    """
    print("\033[91m" + banner + "\033[0m")

def darkrelm_terminal(username, password):
    if verify_vault_password(password):
        original_dir = os.getcwd()
        underworld_terminal_banner()
        print("Type 'exit' to return to main menu")
        print("Commands: ls (list), cd <dir>, download <url> [filename], git <command>, run <file>, pwd (current path)")
        
        while True:
            cmd = input(f"\033[94mUnderWorld@{username}> \033[0m").strip().split()
            if not cmd:
                continue
            
            if cmd[0] == "exit":
                os.chdir(original_dir)
                break
            elif cmd[0] == "ls":
                list_contents()
            elif cmd[0] == "cd" and len(cmd) > 1:
                try:
                    new_dir = cmd[1]
                    if os.path.isabs(new_dir):
                        os.chdir(new_dir)
                    else:
                        os.chdir(os.path.join(os.getcwd(), new_dir))
                    print(f"Changed to: {os.getcwd()}")
                    save_history(f"Changed directory to {os.getcwd()}", username)
                except Exception as e:
                    print(f"\033[91mInvalid directory: {e}\033[0m")
            elif cmd[0] == "download":
                if len(cmd) < 2:
                    print("\033[91mUsage: download <url> [filename]\033[0m")
                else:
                    url = cmd[1]
                    filename = cmd[2] if len(cmd) > 2 else os.path.basename(urllib.parse.urlparse(url).path) or "downloaded_file"
                    try:
                        urllib.request.urlretrieve(url, filename)
                        full_path = os.path.abspath(filename)
                        save_history(f"Downloaded '{filename}' from {url}", username)
                        print(f"\033[92mDownloaded {filename}!\033[0m")
                        if full_path not in SESSION_FILES:
                            SESSION_FILES.append(full_path)
                    except Exception as e:
                        print(f"\033[91mDownload failed: {e}\033[0m")
            elif cmd[0] == "git":
                try:
                    result = subprocess.run(['git'] + cmd[1:], capture_output=True, text=True)
                    print(result.stdout)
                    if result.stderr:
                        print("\033[91m" + result.stderr + "\033[0m")
                    save_history(f"Git command: {' '.join(cmd[1:])}", username)
                except:
                    print("\033[91mGit command failed!\033[0m")
            elif cmd[0] == "run" and len(cmd) > 1:
                try:
                    result = subprocess.run([cmd[1]], capture_output=True, text=True)
                    print(result.stdout)
                    if result.stderr:
                        print("\033[91m" + result.stderr + "\033[0m")
                    save_history(f"Ran program: {cmd[1]}", username)
                except:
                    print("\033[91mRun failed!\033[0m")
            elif cmd[0] == "pwd":
                print(f"Current path: {os.getcwd()}")
            else:
                print("\033[91mUnknown command!\033[0m")
    else:
        print("\033[91mIncorrect password, access denied!\033[0m")

def cleanup():
    print("\033[91mCleaning up all traces...\033[0m")
    for item in SESSION_FILES:
        try:
            if os.path.exists(item):
                if os.path.isfile(item):
                    os.remove(item)
                    print(f"\033[91mDeleted file: {item}\033[0m")
                elif os.path.isdir(item):
                    shutil.rmtree(item)
                    print(f"\033[91mDeleted folder: {item}\033[0m")
        except Exception as e:
            print(f"\033[91mError deleting {item}: {e}\033[0m")
    SESSION_FILES.clear()
    print("\033[91mAll traces removed!\033[0m")

def main():
    welcome_banner()
    username, password = login()
    initialize_vault()

    while True:
        print("\n\033[94mOptions:\033[0m")
        print("1. Create folder in vault")
        print("2. Create file in vault")
        print("3. Delete file/folder in vault")
        print("4. View vault contents")
        print("5. View file contents")
        print("6. Simulate downloads to vault")
        print("7. Enter UnderWorld Terminal")
        print("8. View history")
        print("9. Logout (deletes everything)")
        choice = input("Choose an action (1-9): ")

        if choice == "1":
            if verify_vault_password(password):
                folder_name = input("\033[93mEnter folder name: \033[0m")
                folder_path = os.path.join(VAULT_FOLDER, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                save_history(f"Created folder '{folder_name}' in vault", username)
                print(f"\033[92mFolder '{folder_name}' created in vault!\033[0m")
                if folder_path not in SESSION_FILES:
                    SESSION_FILES.append(folder_path)
            else:
                print("\033[91mIncorrect password, access denied!\033[0m")
        elif choice == "2":
            create_file_in_vault(username, password)
        elif choice == "3":
            delete_item_in_vault(username, password)
        elif choice == "4":
            if not os.path.exists(VAULT_FOLDER):
                print("\033[91mVault not found! Initializing...\033[0m")
                initialize_vault()
            os.chdir(VAULT_FOLDER)
            list_contents()
            os.chdir("..")
        elif choice == "5":
            view_file(username, password)
        elif choice == "6":
            if verify_vault_password(password):
                simulate_downloads(username)
            else:
                print("\033[91mIncorrect password, access denied!\033[0m")
        elif choice == "7":
            darkrelm_terminal(username, password)
        elif choice == "8":
            history = load_history()
            print("\033[96m--- History ---\033[0m")
            if history:
                for entry in history:
                    print(entry)
            else:
                print("No history yet.")
        elif choice == "9":
            save_history("Logged out", username)
            cleanup()
            print("\033[92mGoodbye!\033[0m")
            break
        else:
            print("\033[91mInvalid choice, try again.\033[0m")

if __name__ == "__main__":
    main()