import os
import time

def print_settings():
    """Print environment settings excluding secrets"""
    print("\nCurrent Settings:")
    print("-" * 50)
    for key, value in sorted(os.environ.items()):
        # Skip AWS secret key and any other sensitive data
        if "SECRET" not in key.upper() and "PASSWORD" not in key.upper():
            print(f"{key}={value}")
    print("-" * 50)

if __name__ == "__main__":
    print_settings()
    print("\nContainer is running in debug mode. Use Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting debug mode...")
