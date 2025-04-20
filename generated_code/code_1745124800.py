# Define an empty list to store the todo items
todo_list = []

# Function to add a new todo item
def add_todo():
    new_todo = input("Enter a new todo item: ")
    todo_list.append(new_todo)
    print("Todo item added successfully!")

# Function to display all todo items
def display_todos():
    if todo_list:
        print("Todo List:")
        for index, todo in enumerate(todo_list, start=1):
            print(f"{index}. {todo}")
    else:
        print("Todo List is empty!")

# Function to remove a todo item
def remove_todo():
    display_todos()
    if todo_list:
        index = int(input("Enter the index of the todo item to remove: "))
        if 1 <= index <= len(todo_list):
            removed_todo = todo_list.pop(index - 1)
            print(f"'{removed_todo}' removed from the todo list.")
        else:
            print("Invalid index!")
    else:
        print("Todo List is empty!")

# Main program loop
while True:
    print("\nTodo List App")
    print("1. Add Todo")
    print("2. Display Todos")
    print("3. Remove Todo")
    print("4. Exit")

    choice = input("Enter your choice: ")

    if choice == '1':
        add_todo()
    elif choice == '2':
        display_todos()
    elif choice == '3':
        remove_todo()
    elif choice == '4':
        print("Exiting Todo List App. Goodbye!")
        break
    else:
        print("Invalid choice. Please try again.")