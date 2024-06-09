import multiprocessing
import subprocess
import sys
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


def check_password(stego_file, password):
    password = password.strip()
    try:
        result = subprocess.run(
            ["steghide", "extract", "-sf", stego_file, "-p", password, "-xf", "output.txt"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            return password
    except subprocess.CalledProcessError as e:
        if "could not extract any data" in e.stderr.decode():
            return None
        else:
            return e.stderr.decode()
    return None


def steghide_bruteforce(stego_file, wordlist, max_workers=4):
    try:
        with open(wordlist, 'r', encoding='latin-1') as file:
            passwords = file.readlines()
    except FileNotFoundError:
        print(f"Wordlist file '{wordlist}' not found.")
        return None
    except UnicodeDecodeError as e:
        print(f"Error reading wordlist file '{wordlist}': {e}")
        return None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_password, stego_file, password): password for password in passwords}

        for future in tqdm(as_completed(futures), total=len(passwords), desc="Brute-forcing", unit="password",
                           ncols=100):
            result = future.result()
            if result:
                tqdm.write(f"Password found: {result}")
                return result

    print("Password not found")
    return None


def get_current_thread_count():
    # Returns the number of currently active threads
    return threading.active_count()


def get_cpu_count():
    # Returns the number of logical CPU cores
    return multiprocessing.cpu_count()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python bruteforce_steghide.py <stego_file> <wordlist>")
    else:
        stego_file = sys.argv[1]
        wordlist = sys.argv[2]

        # Clear terminal
        os.system('cls' if os.name == 'nt' else 'clear')

        cpu_count = get_cpu_count()
        print(f"Available logical CPU cores: {cpu_count}")

        # Get the number of threads from the user
        max_workers = int(input(f"Enter the number of threads to use (1-{cpu_count}): "))
        if max_workers < 1 or max_workers > cpu_count:
            print(f"Invalid number of threads. Please enter a number between 1 and {cpu_count}.")
            sys.exit(1)

        # Animation loop
        animation_chars = "|/-\\"
        animation_index = 0

        print(f"Starting brute-force with {max_workers} threads...")
        print(f"Initial thread count: {get_current_thread_count()}")

        # Brute-force process
        for _ in tqdm(range(100), desc="Progress", unit="%", ncols=100, ascii=True):
            time.sleep(0.05)
            animation_index = (animation_index + 1) % len(animation_chars)
            sys.stdout.write("\r" + "Brute-forcing... " + animation_chars[animation_index])
            sys.stdout.flush()

        print()
        result = steghide_bruteforce(stego_file, wordlist, max_workers)

        if result:
            print(f"Password found: {result}")
        else:
            print("Password not found")

        print(f"Final thread count: {get_current_thread_count()}")
