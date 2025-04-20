try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError as e:
    raise ImportError("tkinter is not installed. Please install it using 'pip install tk' to run this program.") from e

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Calculator")

        self.screen = tk.Entry(master, width=35, borderwidth=5)
        self.screen.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        self.buttons = [
            ('7', 1), ('8', 2), ('9', 3), ('/', 4),
            ('4', 5), ('5', 6), ('6', 7), ('*', 8),
            ('1', 9), ('2', 10), ('3', 11), ('-', 12),
            ('0', 13), ('.', 14), ('=', 15), ('+', 16),
        ]

        for btn_text, pos in self.buttons:
            if btn_text == '=':
                self.add_button(btn_text, self.equals, 4, pos)
            else:
                self.add_button(btn_text, lambda btn=btn_text: self.append_to_screen(btn), 4 if btn_text in ('+', '-', '*', '/') else 1, pos)

        self.clear_button = tk.Button(master, text='Clear', command=self.clear_screen)
        self.clear_button.grid(row=5, column=0, columnspan=4, sticky="nsew")

    def add_button(self, text, command, height, position):
        button = tk.Button(self.master, text=text, height=height, command=command)
        button.grid(row=(position-1)//4 + 1, column=(position-1) % 4, sticky="nsew")

    def append_to_screen(self, value):
        self.screen.insert(tk.END, value)

    def clear_screen(self):
        self.screen.delete(0, tk.END)

    def equals(self):
        try:
            result = eval(self.screen.get())
            self.clear_screen()
            self.screen.insert(0, result)
        except Exception as e:
            messagebox.showerror("Error", "Invalid expression")
            self.clear_screen()

def main():
    root = tk.Tk()
    calculator = Calculator(root)

    for i in range(4):
        root.grid_columnconfigure(i, weight=1)
    for i in range(6):
        root.grid_rowconfigure(i, weight=1)

    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")