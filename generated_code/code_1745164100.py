# Since no external libraries are required for this basic calculator, the check_libraries function is unnecessary.

# Define the calculator class
class Calculator:
    def add(self, x, y):
        """Add Function"""
        return x + y

    def subtract(self, x, y):
        """Subtract Function"""
        return x - y

    def multiply(self, x, y):
        """Multiply Function"""
        return x * y

    def divide(self, x, y):
        """Divide Function"""
        if y == 0:
            return "Error! Division by zero."
        return x / y

def main():
    calculator = Calculator()
    while True:
        print("\nOptions:")
        print("Enter 'add' to add two numbers")
        print("Enter 'subtract' to subtract two numbers")
        print("Enter 'multiply' to multiply two numbers")
        print("Enter 'divide' to divide two numbers")
        print("Enter 'quit' to end the program")
        user_input = input(": ").lower()

        if user_input == "quit":
            print("Thank you for using the calculator. Goodbye!")
            break

        # Error handling for the input numbers
        try:
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))
        except ValueError:
            print("Error! Please enter a number.")
            continue

        if user_input == "add":
            print("The result is", calculator.add(num1, num2))
        elif user_input == "subtract":
            print("The result is", calculator.subtract(num1, num2))
        elif user_input == "multiply":
            print("The result is", calculator.multiply(num1, num2))
        elif user_input == "divide":
            result = calculator.divide(num1, num2)
            if result == "Error! Division by zero.":
                print(result)
            else:
                print("The result is", result)
        else:
            print("Unknown input")

if __name__ == "__main__":
    main()