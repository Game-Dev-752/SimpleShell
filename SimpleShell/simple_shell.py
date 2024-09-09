import os
import shutil
import requests
import datetime
import tkinter as tk
from tkinter import scrolledtext
from math import log

class SimpleShell:
    def __init__(self, root):
        self.root = root
        self.root.title("SimpleShell v1.0")
        self.root.configure(bg='black')
        self.root.resizable(False, False)
        self.root.iconbitmap('./assets/SimpleShell.ico')

        self.font = ("Cascadia Mono", 12)
        self.output_area = scrolledtext.ScrolledText(self.root, width=120, height=30, font=self.font, bg="black", fg="white", insertbackground="white")
        self.output_area.pack(pady=5, padx=5)

        self.output_area.bind("<Return>", self.on_enter)
        self.output_area.bind("<KeyPress>", self.on_keypress)

        self.variables = {}
        self.temporary_variables = {}

        self.start_terminal()
        self.output_area.focus_set()

    def operate(self, num1, operation, num2):
        try:
            num1 = float(num1)
            num2 = float(num2)
            if operation == '+':
                return str(num1 + num2)
            elif operation == '-':
                return str(num1 - num2)
            elif operation == '*':
                return str(num1 * num2)
            elif operation == '/':
                if num2 != 0:
                    return str(num1 / num2)
                else:
                    return "Cannot divide by zero."
            elif operation == '**' or operation == '^':
                return str(num1 ** num2)
            elif operation == 'root' or operation == '√':
                return str(num2 ** (1 / num1))
            elif operation == 'log':
                return str(log(num2) / log(num1))
            else:
                return "Unknown operation. Use +, -, *, /, ^/**, root or log."
        except ValueError:
            return "Please provide valid numbers."

    def set_variable(self, scope, variable, value):
        if scope == 'permanent':
            self.variables[variable] = value
            return f"Permanent variable '{variable}' set to '{value}'."
        elif scope == 'temporary':
            self.temporary_variables[variable] = value
            return f"Temporary variable '{variable}' set to '{value}'."
        else:
            return "Unknown scope. Use 'permanent' or 'temporary'."

    def edit_variable(self, variable, new_value):
        if variable in self.variables:
            self.variables[variable] = new_value
            return f"Permanent variable '{variable}' updated to '{new_value}'."
        elif variable in self.temporary_variables:
            self.temporary_variables[variable] = new_value
            return f"Temporary variable '{variable}' updated to '{new_value}'."
        else:
            return f"Variable '{variable}' not found."

    def execute_command(self, command):
        cmd = command.strip().split()
        if not cmd:
            return ""

        command = cmd[0]
        result = ""
        if command == 'make':
            if len(cmd) < 3:
                result = "Usage: make (folder or file) (name) (file extension)"
            else:
                type_ = cmd[1]
                name = cmd[2]
                extension = cmd[3] if len(cmd) > 3 else ''
                result = self.make(type_, name, extension)
        elif command == 'delete':
            if len(cmd) < 2:
                result = "Usage: delete (name)"
            else:
                name = cmd[1]
                result = self.delete(name)
        elif command == 'goto':
            if len(cmd) < 2:
                result = "Usage: goto (directory)"
            else:
                directory = cmd[1]
                result = self.goto(directory)
        elif command == 'print':
            if len(cmd) < 3:
                result = "Usage: print (text) (amount)"
            else:
                text = cmd[1]
                amount = cmd[2]
                result = self.print_text(text, amount)
        elif command == 'inspect':
            result = self.inspect()
        elif command == 'operate':
            if len(cmd) < 4:
                result = "Usage: operate (num1) (operation) (num2)"
            else:
                num1 = cmd[1]
                operation = cmd[2]
                num2 = cmd[3]
                result = self.operate(num1, operation, num2)
        elif command == 'set':
            if len(cmd) < 4:
                result = "Usage: set (permanent or temporary) (variable) (value)"
            else:
                scope = cmd[1]
                variable = cmd[2]
                value = " ".join(cmd[3:])
                result = self.set_variable(scope, variable, value)
        elif command == 'edit':
            if len(cmd) < 3:
                result = "Usage: edit (variable) (new_value)"
            else:
                variable = cmd[1]
                new_value = " ".join(cmd[2:])
                result = self.edit_variable(variable, new_value)
        elif command == 'remove':
            if len(cmd) < 2:
                result = "Usage: remove (variable)"
            else:
                variable = cmd[1]
                result = self.remove_variable(variable)
        elif command == 'rename':
            if len(cmd) < 3:
                result = "Usage: rename (old_name) (new_name)"
            else:
                old_name = cmd[1]
                new_name = cmd[2]
                result = self.rename(old_name, new_name)
        elif command == 'copy':
            if len(cmd) < 3:
                result = "Usage: copy (source) (destination)"
            else:
                source = cmd[1]
                destination = cmd[2]
                result = self.copy(source, destination)
        elif command == 'move':
            if len(cmd) < 3:
                result = "Usage: move (source) (destination)"
            else:
                source = cmd[1]
                destination = cmd[2]
                result = self.move(source, destination)
        elif command == 'date':
            result = self.date()
        elif command == 'echo':
            if len(cmd) < 2:
                result = "Usage: echo (text)"
            else:
                text = " ".join(cmd[1:])
                result = self.echo(text)
        elif command == 'clear':
            self.clear()
            return ""
        elif command == 'read':
            if len(cmd) < 2:
                result = "Usage: read (file)"
            else:
                file = cmd[1]
                result = self.read(file)
        elif command == 'find':
            if len(cmd) < 2:
                result = "Usage: find (name)"
            else:
                name = cmd[1]
                result = self.find(name)
        elif command == 'download':
            if len(cmd) < 2:
                result = "Usage: download (url)"
            else:
                url = cmd[1]
                result = self.download(url)
        elif command == 'upload':
            if len(cmd) < 2:
                result = "Usage: upload (file)"
            else:
                file = cmd[1]
                result = self.upload(file)
        elif command == 'run':
            if len(cmd) < 2:
                result = "Usage: run (file name with .sshell as the extension)"
            else:
                file = cmd[1]
                result = self.run_file(file)
        elif command == 'help':
            if len(cmd) < 2:
                result = self.help()
            else:
                result = self.help(cmd[1])
        else:
            result = "Unknown command. Type 'help' for a list of commands."

        return f"\n{result}\n--------------------------------"

    def run_file(self, filename):
        if not filename.endswith('.sshell'):
            return "Error: File must have a .sshell extension."
        
        if not os.path.isfile(filename):
            return f"Error: File '{filename}' does not exist."
        
        with open(filename, 'r') as file:
            commands = file.readlines()
        
        results = []
        for command in commands:
            command = command.strip()
            if command:
                results.append(self.execute_command(command))
        
        return "\n".join(results)

    def start_terminal(self):
        self.output_area.insert(tk.END, "SimpleShell v1.0 - Type 'help' for a list of commands\n\n")
        self.output_area.insert(tk.END, f"{os.getcwd()} >>> ")
        self.output_area.mark_set("insert", tk.END)
        self.output_area.see(tk.END)

    def on_enter(self, event):
        command = self.output_area.get("insert linestart", tk.END).strip().split(">>> ")[-1]
        self.output_area.insert(tk.END, "\n" + self.execute_command(command) + "\n")
        self.output_area.insert(tk.END, f"{os.getcwd()} >>> ")
        self.output_area.mark_set("insert", tk.END)
        self.output_area.see(tk.END)
        return "break"

    def on_keypress(self, event):
        if event.keysym == "BackSpace":
            self.output_area.mark_set("insert", tk.END)
        elif event.keysym == "Up":
            pass
        elif event.keysym == "Down":
            pass
        elif event.keysym == "Left":
            pass
        elif event.keysym == "Right":
            pass
        elif event.keysym == "Return":
            pass

    def make(self, type_, name, extension=''):
        try:
            if type_ == 'file':
                with open(f"{name}.{extension}", 'w') as f:
                    return f"File '{name}.{extension}' created."
            elif type_ == 'folder':
                os.makedirs(name, exist_ok=True)
                return f"Folder '{name}' created."
            else:
                return "Invalid type. Use 'file' or 'folder'."
        except Exception as e:
            return f"Error: {e}"

    def delete(self, name):
        try:
            if os.path.isfile(name):
                os.remove(name)
                return f"File '{name}' deleted."
            elif os.path.isdir(name):
                shutil.rmtree(name)
                return f"Folder '{name}' deleted."
            else:
                return f"'{name}' does not exist."
        except Exception as e:
            return f"Error: {e}"

    def goto(self, directory):
        try:
            os.chdir(directory)
            return f"Changed directory to '{directory}'."
        except Exception as e:
            return f"Error: {e}"

    def print_text(self, text, amount):
        try:
            amount = int(amount)
            return text * amount
        except ValueError:
            return "Error: 'amount' must be an integer."

    def inspect(self):
        return f"Current directory: {os.getcwd()}\nFiles:\n" + "\n".join(os.listdir(os.getcwd()))

    def remove_variable(self, variable):
        if variable in self.variables:
            del self.variables[variable]
            return f"Permanent variable '{variable}' removed."
        elif variable in self.temporary_variables:
            del self.temporary_variables[variable]
            return f"Temporary variable '{variable}' removed."
        else:
            return f"Variable '{variable}' not found."

    def rename(self, old_name, new_name):
        try:
            os.rename(old_name, new_name)
            return f"Renamed '{old_name}' to '{new_name}'."
        except Exception as e:
            return f"Error: {e}"

    def copy(self, source, destination):
        try:
            if os.path.isfile(source):
                shutil.copy(source, destination)
                return f"Copied file '{source}' to '{destination}'."
            elif os.path.isdir(source):
                shutil.copytree(source, destination)
                return f"Copied folder '{source}' to '{destination}'."
            else:
                return f"'{source}' does not exist."
        except Exception as e:
            return f"Error: {e}"

    def move(self, source, destination):
        try:
            shutil.move(source, destination)
            return f"Moved '{source}' to '{destination}'."
        except Exception as e:
            return f"Error: {e}"

    def date(self):
        return str(datetime.datetime.now())

    def echo(self, text):
        return text

    def clear(self):
        self.output_area.delete('1.0', tk.END)

    def read(self, file):
        try:
            with open(file, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error: {e}"

    def find(self, name):
        result = []
        for root, dirs, files in os.walk(os.getcwd()):
            if name in files:
                result.append(os.path.join(root, name))
            if name in dirs:
                result.append(os.path.join(root, name))
        return "\n".join(result) if result else f"No results found for '{name}'."

    def download(self, url):
        try:
            response = requests.get(url)
            filename = url.split("/")[-1]
            with open(filename, 'wb') as file:
                file.write(response.content)
            return f"Downloaded file '{filename}' from '{url}'."
        except Exception as e:
            return f"Error: {e}"

    def upload(self, file):
        return f"Upload functionality is not implemented in this version."

    def help(self, topic=None):
        if not topic:
            return (
                "Available commands:\n"
                "1. make (folder or file) (name) (file extension)\n"
                "2. delete (name)\n"
                "3. goto (directory)\n"
                "4. print (text) (amount)\n"
                "5. inspect\n"
                "6. operate (num1) (operation) (num2)\n"
                "7. set (permanent or temporary) (variable) (value)\n"
                "8. edit (variable) (new_value)\n"
                "9. remove (variable)\n"
                "10. rename (old_name) (new_name)\n"
                "11. copy (source) (destination)\n"
                "12. move (source) (destination)\n"
                "13. date\n"
                "14. echo (text)\n"
                "15. clear\n"
                "16. read (file)\n"
                "17. find (name)\n"
                "18. download (url)\n"
                "19. upload (file)\n"
                "20. run (file name with .sshell as the extension)\n"
                "21. help (command)"
            )
        else:
            return f"No specific help available for '{topic}'."

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleShell(root)
    root.mainloop()
