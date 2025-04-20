import tkinter as tk

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Calculator")

        # Entry widget for the user input
        self.screen = tk.Entry(master, width=35, borderwidth=5)
        self.screen.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        # Mapping buttons to their respective values
        buttons = [
            ('7', 1), ('8', 2), ('9', 3), ('/', 4),
            ('4', 5), ('5', 6), ('6', 7), ('*', 8),
            ('1', 9), ('2', 10), ('3', 11), ('-', 12),
            ('0', 13), ('C', 14), ('=', 15), ('+', 16),
        ]

        # Adding buttons to the GUI
        for button_text, pos in buttons:
            button_command = lambda x=button_text: self.click(x)
            tk.Button(master, text=button_text, width=9, height=3, command=button_command).grid(row=(pos-1)//4 + 1, column=(pos-1)%4)

    def click(self, value):
        """Handle button click events."""
        if value == "=":
            try:
                # Attempt to evaluate the expression in the entry widget
                result = str(eval(self.screen.get()))
                self.screen.delete(0, tk.END)
                self.screen.insert(0, result)
            except Exception:
                self.screen.delete(0, tk.END)
                self.screen.insert(0, "Error")
        elif value == "C":
            # Clear the entry widget
            self.screen.delete(0, tk.END)
        else:
            # Append the button's value to the entry widget
            self.screen.insert(tk.END, value)

def main():
    root = tk.Tk()
    calculator = Calculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()