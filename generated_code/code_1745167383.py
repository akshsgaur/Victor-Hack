import sys
import os
import platform
import subprocess

def check_and_install(package_name):
    """
    Check if a package is installed; if not, prompt the user to install it.
    """
    try:
        __import__(package_name)
        print(f"'{package_name}' is already installed.")
    except ImportError:
        print(f"'{package_name}' is not installed.")
        choice = input(f"Would you like to install '{package_name}' now? (y/n): ").strip().lower()
        if choice == 'y':
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                print(f"Successfully installed '{package_name}'.")
            except subprocess.CalledProcessError:
                print(f"Failed to install '{package_name}'. Please install it manually.")
                sys.exit(1)
        else:
            print(f"Please install '{package_name}' and rerun the script.")
            sys.exit(1)

# Check for required external libraries
required_libraries = ['psutil']
for lib in required_libraries:
    check_and_install(lib)

import psutil

def get_os_info():
    """
    Retrieve and display basic OS information.
    """
    try:
        os_name = platform.system()
        os_release = platform.release()
        os_version = platform.version()
        architecture = platform.machine()
        print(f"Operating System: {os_name}")
        print(f"Release: {os_release}")
        print(f"Version: {os_version}")
        print(f"Architecture: {architecture}")
    except Exception as e:
        print(f"Error retrieving OS info: {e}")

def list_processes():
    """
    List all running processes with their PID and name.
    """
    try:
        print(f"{'PID':<10} {'Process Name'}")
        for proc in psutil.process_iter(['pid', 'name']):
            pid = proc.info.get('pid', 'N/A')
            name = proc.info.get('name', 'N/A')
            print(f"{pid:<10} {name}")
    except Exception as e:
        print(f"Error listing processes: {e}")

def create_directory(path):
    """
    Create a directory at the specified path.
    """
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Directory created or already exists at: {path}")
    except Exception as e:
        print(f"Error creating directory '{path}': {e}")

def delete_directory(path):
    """
    Delete the directory at the specified path.
    """
    try:
        if os.path.isdir(path):
            os.rmdir(path)
            print(f"Directory '{path}' has been deleted.")
        else:
            print(f"Directory '{path}' does not exist.")
    except Exception as e:
        print(f"Error deleting directory '{path}': {e}")

def create_file(file_path, content=""):
    """
    Create a file with optional content.
    """
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"File created at: {file_path}")
    except Exception as e:
        print(f"Error creating file '{file_path}': {e}")

def delete_file(file_path):
    """
    Delete the specified file.
    """
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"File '{file_path}' has been deleted.")
        else:
            print(f"File '{file_path}' does not exist.")
    except Exception as e:
        print(f"Error deleting file '{file_path}': {e}")

def get_disk_usage():
    """
    Display disk usage statistics.
    """
    try:
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                print(f"Device: {partition.device}")
                print(f"  Mountpoint: {partition.mountpoint}")
                print(f"  File system type: {partition.fstype}")
                print(f"  Total Size: {usage.total / (1024 ** 3):.2f} GB")
                print(f"  Used: {usage.used / (1024 ** 3):.2f} GB")
                print(f"  Free: {usage.free / (1024 ** 3):.2f} GB")
                print(f"  Percentage Used: {usage.percent}%\n")
            except Exception as e:
                print(f"Error retrieving disk usage for {partition.device}: {e}")
    except Exception as e:
        print(f"Error retrieving disk partitions: {e}")

def main():
    """
    Main function to run the OS simulation.
    """
    print("=== Operating System Simulation ===")
    get_os_info()
    print("\nListing processes:")
    list_processes()
    print("\nCreating a test directory 'test_dir':")
    create_directory('test_dir')
    print("\nCreating a test file 'test_dir/test_file.txt':")
    create_file('test_dir/test_file.txt', content="This is a test file.")
    print("\nDisk usage information:")
    get_disk_usage()
    print("\nCleaning up: deleting test file and directory.")
    delete_file('test_dir/test_file.txt')
    delete_directory('test_dir')
    print("=== End of Simulation ===")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")