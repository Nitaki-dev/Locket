import tkinter, pyperclip, sv_ttk, base64, hashlib, sys, ast, ctypes as ct
from tkinter import ttk, messagebox
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

isFixed = False

def generate_salt(password, salt_length=16):
    hashed_password = hashlib.sha256(password.encode()).digest()
    return hashed_password[:salt_length]

def derive_key(password, salt, key_length=32):
    return PBKDF2(password, salt, dkLen=key_length)

def encrypt(key, data):
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

def decrypt(key, data):
    data = base64.b64decode(data)
    nonce = data[:16]
    tag = data[16:32]
    ciphertext = data[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode()

tree_data = []
key = ''
salt = generate_salt(key)
user_key = derive_key(key.encode(), salt)
file_selected = 0

def save_passwords():
    open(f'pass-{file_selected}', 'w').close()
    file = open(f'pass-{file_selected}', 'w')

    i = 0
    for item in tree_data:
        message = str(tree_data[i])
        encMessage = encrypt(user_key, message)
        file.write(str(encMessage) + '\n')
        i+=1

def load_passwords():
    global tree_data
    for i in range(5):
        print(i)
        try:
            file = open(f'pass-{i}', 'r')
            tree_data = []

            try:
                for x in file:
                    line = decrypt(user_key, x)
                    tree_data += [ast.literal_eval(line)]

                global file_selected
                file_selected = i

                print(f'Loaded file number {i}')
                break
            except:
                print(f'Wrong password for {i}')
        except:
            print("No file found, creating new one...")
            f = open(f'pass-{i}', 'x')
            file_selected = i
            tree_data = [
                ("Service", ("Email/Username", "Password")),
                ("____________________________________", ("____________________________________", "____________________________________"))
            ]
            save_passwords()
            break

def new_input(name, username, password, password_list_instance):
    global tree_data
    tree_data.append((name, (username, password)))
    
    save_passwords()
    password_list_instance.update_tree()

class new_entry(ttk.Frame):
    def __init__(self, parent, password_list_instance):
        super().__init__(parent, style="Card.TFrame", padding=15)
        self.password_list = password_list_instance
        self.columnconfigure(0, weight=1)
        self.add_widgets()

    def add_widgets(self):
        ttk.Label(self, text="Service").grid(row=0, column=0, padx=5, pady=(0, 2), sticky="w")
        ttk.Label(self, text="Username/Email").grid(row=2, column=0, padx=5, pady=(0, 2), sticky="w")
        ttk.Label(self, text="Password").grid(row=4, column=0, padx=5, pady=(0, 2), sticky="w")

        self.app = ttk.Entry(self)
        self.app.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="ew")
        
        self.username = ttk.Entry(self)
        self.username.grid(row=3, column=0, padx=5, pady=(0, 10), sticky="ew")
        
        self.password = ttk.Entry(self, show="*")
        self.password = ttk.Entry(self)
        self.password.grid(row=5, column=0, padx=5, pady=(0, 10), sticky="ew")

        self.button = ttk.Button(self, text="Add password", command=self.add_password, style="Accent.TButton")
        self.button.grid(row=6, column=0, padx=5, pady=(10, 0), sticky="ew")

    def add_password(self):
        application = self.app.get()
        username = self.username.get()
        password = self.password.get()
        
        if (application=="" or username=="" or password==""): return

        self.app.delete(0, 'end')
        self.username.delete(0, 'end')
        self.password.delete(0, 'end')

        new_input(application, username, password, self.password_list)        

class password_list(ttk.PanedWindow):
    def __init__(self, parent):
        super().__init__(parent)

        self.pane_1 = ttk.Frame(self, padding=(0, 0, 0, 0))
        self.add(self.pane_1, weight=1)

        self.add_widgets()
        self.update_tree()

    def add_widgets(self):
        self.scrollbar = ttk.Scrollbar(self.pane_1)
        self.scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            self.pane_1,
            columns=(1, 2),
            height=12,
            selectmode="browse",
            show=("tree",),
            yscrollcommand=self.scrollbar.set,
        )

        self.scrollbar.config(command=self.tree.yview)

        self.tree.pack(expand=False, fill="both")

        self.tree.column("#0", anchor="w", width=110)
        self.tree.column(1, anchor="w", width=130)
        self.tree.column(2, anchor="w", width=120)

        self.update_tree()

        self.tree.bind("<Button-1>", self.copy_to_clipboard)
        self.tree.bind("<Button-3>", self.edit_or_delete_menu)
        # self.tree.bind("<Double-1>", self.edit_item)

    def copy_to_clipboard(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            column = self.tree.identify_column(event.x)
            app_name = self.tree.item(item, "text")
            if column == "#1":
                value = self.tree.item(item, "values")[0]
                messagebox.showinfo("Password manager", f"{app_name} username copied to clipboard")
                pyperclip.copy(value)
            elif column == "#2":
                value = self.tree.item(item, "values")[1]
                messagebox.showinfo("Password manager", f"{app_name} password copied to clipboard")
                pyperclip.copy(value)

    def edit_or_delete_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            menu = tkinter.Menu(self.tree, tearoff=0)
            menu.add_command(label="Edit", command=lambda: self.edit_item(item))
            menu.add_command(label="Delete", command=lambda: self.delete_item(item))
            menu.post(event.x_root, event.y_root)

    def delete_item(self, item):
        confirm = messagebox.askyesno("Delete Item", "Are you sure you want to delete this item?")
        if confirm:
            app_name = self.tree.item(item, "text")
            for index, entry in enumerate(tree_data):
                if entry[0] == app_name:
                    del tree_data[index]
                    break
            self.tree.delete(item)
            save_passwords()

    def edit_item(self, item):
        current_values = self.tree.item(item, "values")
        app_name = self.tree.item(item, "text")

        edit_window = tkinter.Toplevel(self)
        edit_window.title("Edit Item")

        ttk.Label(edit_window, text="Service").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(edit_window, text="Username").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(edit_window, text="Password").grid(row=2, column=0, padx=5, pady=5, sticky="w")

        app_entry = ttk.Entry(edit_window, width=30)
        app_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        app_entry.insert(0, app_name)

        username_entry = ttk.Entry(edit_window, width=30)
        username_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        username_entry.insert(0, current_values[0])

        password_entry = ttk.Entry(edit_window, width=30)
        password_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        password_entry.insert(0, current_values[1])

        def update_values():
            new_values = (username_entry.get(), password_entry.get())
            self.tree.item(item, values=new_values)
            for index, entry in enumerate(tree_data):
                if entry[0] == app_name:
                    updated_entry = (app_name, new_values)
                    tree_data[index] = updated_entry
                    break
            save_passwords()
            edit_window.destroy()

        update_button = ttk.Button(edit_window, text="Update", command=update_values)
        update_button.grid(row=3, columnspan=2, padx=5, pady=10)

    def update_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for item in tree_data:
            if len(item) == 2:
                name, (desc, other) = item
                self.tree.insert("", "end", text=name, values=(desc, other))
            else:
                name = item[0]
                self.tree.insert("", "end", text=name, values=("", ""))

class App(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=15)

        for index in range(2):
            self.columnconfigure(index, weight=1)
            self.rowconfigure(index, weight=1)

        password_list_instance = password_list(self)
        new_entry(self, password_list_instance).grid(row=0, column=1, rowspan=2, padx=10, pady=(10, 0), sticky="nsew")
        password_list_instance.grid(row=0, column=2, rowspan=2, padx=10, pady=(10, 0), sticky="nsew")

def main_application():
    load_passwords()

    root = tkinter.Tk()
    root.title("Password manager")
    root.resizable(False, False)

    App(root).pack(expand=True, fill="both")
    
    if isFixed: sv_ttk.set_theme("dark")


    root.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(root.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value), ct.sizeof(value))
    if sys.getwindowsversion().build <= 22000:
        root.withdraw()
        root.deiconify()

    root.mainloop()

def prompt_user_for_password():
    def get_password():
        password = pass_entry.get()
        if password:
            global salt
            global user_key

            key = password
            salt = generate_salt(key)
            user_key = derive_key(key.encode(), salt)
            root.destroy()
            main_application()

    root = tkinter.Tk()
    root.title("Password manager")
    root.geometry("300x128")
    root.resizable(False, False)

    pass_lable = ttk.Label(root, text="Enter your password")
    pass_lable.pack(pady=5)

    pass_entry = ttk.Entry(root, show='*')
    pass_entry.pack(pady=5)

    button = ttk.Button(root, text="Enter Password", command=get_password)
    button.pack(pady=10)

    if isFixed: sv_ttk.set_theme("dark")
    
    root.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(root.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value), ct.sizeof(value))
    if sys.getwindowsversion().build <= 22000:
        root.withdraw()
        root.deiconify()

    root.mainloop()
    
if __name__ == "__main__":
    prompt_user_for_password()