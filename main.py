import os
import sys
from src.train_model import main as train_model_script

def run_website():
    python_path = sys.executable
    os.system(f'"{python_path}" -m streamlit run website/app.py')

if __name__ == "__main__":
    print("1. Train model")
    print("2. Run website")

    choice = input("Enter choice: ")

    if choice == "1":
        train_model_script()
    elif choice == "2":
        run_website()
    else:
        print("Invalid choice")
