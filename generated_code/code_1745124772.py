import random
import string

def generate_password(length):
    # Define the characters to choose from for the password
    characters = string.ascii_letters + string.digits + string.punctuation
    
    # Generate the password by randomly selecting characters from the defined set
    password = ''.join(random.choice(characters) for i in range(length))
    
    return password

# Specify the length of the password
password_length = 12

# Generate and print the password
password = generate_password(password_length)
print("Generated Password:", password)