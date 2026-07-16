import os
import sys

def initialize_project():
    """Ensure all required directories exist."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    directories = [
        "agent",
        "config",
        "credentials",
        "templates",
        "logs"
    ]
    for directory in directories:
        dir_path = os.path.join(base_dir, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

if __name__ == "__main__":
    initialize_project()
    try:
        from main import main
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
