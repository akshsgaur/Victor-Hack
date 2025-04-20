try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError as e:
    raise ImportError("tkinter is not installed. Please install it by running 'sudo apt-get install python3-tk' on Linux or use your system's package manager.") from e

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List App")

        # Frame for the listbox and scrollbar
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        # Listbox to display tasks
        self.listbox = tk.Listbox(self.frame, width=50, height=10, bd=0, fg="#464646", highlightthickness=0, selectbackground="#a6a6a6", activestyle="none")
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        # Scrollbar for the listbox
        self.scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Link scrollbar to listbox
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        # Entry box to add new tasks
        self.entry = tk.Entry(self.root, font=("Helvetica", 24))
        self.entry.pack(pady=20)

        # Add Task button
        self.addTaskBtn = tk.Button(self.root, text="Add Task", command=self.add_task)
        self.addTaskBtn.pack(pady=20)

        # Delete Task button
        self.delTaskBtn = tk.Button(self.root, text="Delete Task", command=self.delete_task)
        self.delTaskBtn.pack(pady=20)

    def add_task(self):
        task = self.entry.get()
        if task.strip():
            self.listbox.insert(tk.END, task)
            self.entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Empty Entry", "Please enter a task.")

    def delete_task(self):
        try:
            selected_task_index = self.listbox.curselection()
            if selected_task_index:
                self.listbox.delete(selected_task_index)
            else:
                messagebox.showwarning("Selection Error", "Please select a task to delete.")
        except Exception as e:
            messagebox.showwarning("Error", f"An error occurred: {e}")

def main():
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")