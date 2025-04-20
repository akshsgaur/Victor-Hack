import sys
import subprocess

def check_and_install(package):
    """
    Check if a package is installed; if not, attempt to install it.
    """
    try:
        __import__(package)
    except ImportError:
        print(f"Package '{package}' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Package '{package}' installed successfully.")
    except Exception as e:
        print(f"An unexpected error occurred while checking/installing '{package}': {e}")
        sys.exit(1)

# Check and install required external libraries
required_packages = ['numpy']
for pkg in required_packages:
    check_and_install(pkg)

import numpy as np

def sub(array1, array2):
    """
    Element-wise subtraction of two arrays.
    
    Parameters:
        array1 (list or np.ndarray): The first input array.
        array2 (list or np.ndarray): The second input array.
        
    Returns:
        np.ndarray: The result of element-wise subtraction.
        
    Raises:
        ValueError: If input arrays are not compatible for subtraction.
    """
    try:
        # Convert inputs to numpy arrays for element-wise operations
        arr1 = np.array(array1)
        arr2 = np.array(array2)
        
        # Check if shapes are compatible
        if arr1.shape != arr2.shape:
            raise ValueError(f"Input arrays must have the same shape. Got {arr1.shape} and {arr2.shape}.")
        
        # Perform element-wise subtraction
        result = np.subtract(arr1, arr2)
        return result
    except Exception as e:
        print(f"Error during subtraction: {e}")
        raise

if __name__ == "__main__":
    # Example usage
    try:
        # Sample input arrays
        array1 = [1, 2, 3, 4]
        array2 = [4, 3, 2, 1]
        
        # Perform subtraction
        result = sub(array1, array2)
        print("Result of subtraction:", result)
    except Exception as e:
        print(f"An error occurred in main execution: {e}")