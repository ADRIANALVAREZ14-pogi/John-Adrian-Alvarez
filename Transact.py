import tkinter as tk # Main GUI module para sa paggawa ng windows at widgets
from tkinter import messagebox # Para sa mga pop-up messages likes errors, info, at warning
from tkinter import ttk # Themed Tkinter para sa enhanced widgets (Treeview, box)
from datetime import date # Para sa date handling pagkuha ng current date
import os, sys # Operating system interfaces like files/systems
import calendar # Para sa month names at dates
from collections import defaultdict # Para sa dictionary na automatic nagkakameron ng default values

# RESOURCE PATH for EXECUTABLE FILE
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# FILE STORAGE AT DATA MANAGEMENT
TRANSACTIONS_FOLDER = "transaction_records"

# creating folder para sa mga transaction records kung wala pa
if not os.path.exists(TRANSACTIONS_FOLDER):
    os.makedirs(TRANSACTIONS_FOLDER)

SAVE_FILE = os.path.join(TRANSACTIONS_FOLDER, "transactions.txt")

def load_transactions():
    # Naglo-load ng mga transaction from text file
    if not os.path.exists(SAVE_FILE):
        return []

    loaded = []
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                # divides the data using the pipe character
                d, cell, ttype, amount = line.strip().split("|")
                loaded.append({
                    "date": d,
                    "cell": cell,
                    "type": ttype,
                    "amount": float(amount)
                })
            except:
                continue
    return loaded

def save_transactions():
    # saving transactions dun sa text file
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        for t in transactions:
            f.write(f"{t['date']}|{t['cell']}|{t['type']}|{t['amount']}\n")

def show_transaction_folder():
    # Binubuksan ang folder ng transaction records
    try:
        os.startfile(TRANSACTIONS_FOLDER)  # Para sa Windows
    except:
        try:
            os.system(f'open "{TRANSACTIONS_FOLDER}"')  # Para sa macOS
        except:
            try:
                os.system(f'xdg-open "{TRANSACTIONS_FOLDER}"')  # Para sa Linux
            except:
                messagebox.showinfo(
                    "Folder Location",
                    f"Transaction folder:\n{os.path.abspath(TRANSACTIONS_FOLDER)}"
                )

# view the existing transactions
transactions = load_transactions()

# FUNCTIONS PARA SA GUI
def update_display(filtered_transactions=None):
    # updating display of transaction history
    for row in tree.get_children():
        tree.delete(row)
    
    # Gumagamit ng filtered transactions kung meron, kung wala lahat ng transactions
    display_data = filtered_transactions if filtered_transactions is not None else transactions

    for t in display_data:
        # Nagdi-display ng amount na may + para sa income at - para sa expenses
        amount = f"+{t['amount']:.2f}" if t["type"] == "in" else f"-{t['amount']:.2f}"
        tree.insert("", "end", values=(t["date"], t["cell"], amount))

def add_transaction():
    # adding new transaction
    cell = cell_entry.get().strip()
    ttype = type_var.get()

    # Validation for amount
    try:
        amt = float(amount_entry.get())
        if amt <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Invalid amount.")
        return

    # Validation for description
    if not cell:
        messagebox.showerror("Error", "Please enter a description.")
        return

    # creating new transaction
    transactions.append({
        "cell": cell,
        "type": ttype,
        "amount": amt,
        "date": str(date.today())
    })

    # save and update the display
    save_transactions()
    update_display()

    # cleaning input fields
    cell_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)

    messagebox.showinfo("Success", "Transaction saved successfully!")

def delete_transaction():
    # Nagde-delete ng selected transaction
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("No selection", "Please select a transaction to delete.")
        return

    # collecting data from selected transaction
    values = tree.item(selected, "values")
    date_val, desc_val, amount_val = values

    # confirmation bago mag-delete
    if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete this transaction?\n\n{desc_val}\n{amount_val}"):
        return

    # deleting transaction
    for t in transactions:
        if t["date"] == date_val and t["cell"] == desc_val:
            if f"+{t['amount']:.2f}" == amount_val or f"-{t['amount']:.2f}" == amount_val:
                transactions.remove(t)
                break

    save_transactions()
    update_display()
    messagebox.showinfo("Deleted", "Transaction removed successfully.")

def show_analytics():
    # nagddisplay ng financial analytics
    if not transactions:
        messagebox.showinfo("Analytics", "No transaction data available.")
        return

    # for computing ng total income at expenses
    total_in = sum(t["amount"] for t in transactions if t["type"] == "in")
    total_out = sum(t["amount"] for t in transactions if t["type"] == "out")
    net = total_in - total_out

    # Gumagawa ng daily at monthly summaries
    daily = defaultdict(float)
    monthly = defaultdict(float)

    for t in transactions:
        daily[t["date"]] += t["amount"] if t["type"] == "in" else -t["amount"]
        m = t["date"][:7]  # Kumukuha ng year-month
        monthly[m] += t["amount"] if t["type"] == "in" else -t["amount"]

    # creating new window for analytics
    win = tk.Toplevel(root)
    win.title("Analytics Summary")
    win.geometry("500x600")
    win.transient(root)
    win.grab_set()

    try:
        win.iconbitmap(resource_path("fol.ico"))
    except:
        pass

    # Text widget for analytics
    text = tk.Text(win, width=60, height=35)
    text.pack(padx=20, pady=20)

    # Financial summary
    text.insert(tk.END, " FINANCIAL SUMMARY:\n\n")
    text.insert(tk.END, f"Total Cash In: ₱{total_in:,.2f}\n")
    text.insert(tk.END, f"Total Cash Out: ₱{total_out:,.2f}\n")
    text.insert(tk.END, f"Net Balance: ₱{net:,.2f}\n\n")

    # Daily summary
    text.insert(tk.END, " DAILY SUMMARY:\n")
    for d, amt in sorted(daily.items()):
        text.insert(tk.END, f"{d}: ₱{amt:,.2f}\n")

    # Monthly summary
    text.insert(tk.END, "\n MONTHLY SUMMARY:\n")
    for m, amt in sorted(monthly.items()):
        y, mo = m.split("-")
        text.insert(tk.END, f"{calendar.month_name[int(mo)]} {y}: ₱{amt:,.2f}\n")

    text.config(state="disabled")

def search_transactions():
    # Search function para hanapin ang mga transactions
    search_term = search_entry.get().strip().lower()
    
    if not search_term:
        # Kung walang search term, ipakita lahat
        update_display()
        return
    
    # Filter transactions based on search term
    filtered = []
    for t in transactions:
        # Hanapin sa description at date
        if (search_term in t["cell"].lower() or 
            search_term in t["date"].lower() or
            search_term in t["type"].lower()):
            filtered.append(t)
    
    if not filtered:
        messagebox.showinfo("Search Result", "No transactions found matching your search.")
    
    update_display(filtered)

def clear_search():
    # Clear search and show all transactions
    search_entry.delete(0, tk.END)
    update_display()

# UNANG GUI WINDOW
root = tk.Tk()
root.title("TCASH")

try:
    root.iconbitmap(resource_path("fol.ico"))
except:
    pass

# Centering ng window sa screen
window_width = 900
window_height = 700  # Increased height to accommodate search section
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.minsize(800, 600)

# MGA LAYOUT SECTIONS NG GUI
main_frame = tk.Frame(root)
main_frame.pack(expand=True, fill="both", padx=30, pady=20)

# Title section
title_frame = tk.Frame(main_frame)
title_frame.pack(fill="x", pady=15)

tk.Label(
    title_frame,
    text="TCASH",
    font=("Arial", 18, "bold"),
    fg="#2c3e50"
).pack()

# Search section
search_frame = tk.Frame(main_frame, relief="groove", bd=1, padx=20, pady=15)
search_frame.pack(fill="x", pady=10)

tk.Label(
    search_frame, 
    text="Search Transactions:", 
    font=("Arial", 11, "bold"),
    fg="#2c3e50"
).pack(anchor="w", pady=(0, 8))

search_input_frame = tk.Frame(search_frame)
search_input_frame.pack(fill="x")

search_entry = tk.Entry(
    search_input_frame, 
    width=40, 
    font=("Arial", 11),
    bg="#f8f9fa"
)
search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

# Search buttons
search_button_frame = tk.Frame(search_input_frame)
search_button_frame.pack(side="right")

tk.Button(
    search_button_frame,
    text="Search",
    command=search_transactions,
    bg="#3498db",
    fg="white",
    font=("Arial", 10, "bold"),
    width=10
).pack(side="left", padx=5)

tk.Button(
    search_button_frame,
    text="Clear",
    command=clear_search,
    bg="#95a5a6",
    fg="white",
    font=("Arial", 10, "bold"),
    width=10
).pack(side="left", padx=5)

# Bind Enter key to search
search_entry.bind('<Return>', lambda event: search_transactions())

# Input box section
input_frame = tk.Frame(main_frame, relief="groove", bd=1, padx=20, pady=15)
input_frame.pack(fill="x", pady=15)

# Description input
desc_frame = tk.Frame(input_frame)
desc_frame.pack(fill="x", pady=8)

tk.Label(desc_frame, text="Description:", font=("Arial", 11), width=12, anchor="e")\
    .pack(side="left", padx=(0, 10))

cell_entry = tk.Entry(desc_frame, width=35, font=("Arial", 11))
cell_entry.pack(side="left", fill="x", expand=True)

# Type input (income/expense)
type_frame = tk.Frame(input_frame)
type_frame.pack(fill="x", pady=8)

tk.Label(type_frame, text="Type:", font=("Arial", 11), width=12, anchor="e")\
    .pack(side="left", padx=(0, 10))

type_var = tk.StringVar(value="in")
type_menu = ttk.Combobox(
    type_frame, textvariable=type_var,
    values=["in", "out"],
    state="readonly", width=33, font=("Arial", 11)
)
type_menu.pack(side="left", fill="x", expand=True)

# Amount input
amount_frame = tk.Frame(input_frame)
amount_frame.pack(fill="x", pady=8)

tk.Label(amount_frame, text="Amount (₱):", font=("Arial", 11), width=12, anchor="e")\
    .pack(side="left", padx=(0, 10))

amount_entry = tk.Entry(amount_frame, width=35, font=("Arial", 11))
amount_entry.pack(side="left", fill="x", expand=True)

# Action buttons section
button_frame = tk.Frame(main_frame)
button_frame.pack(pady=20)

# Add transaction button
tk.Button(
    button_frame, text="Add Transaction", command=add_transaction,
    bg="#27ae60", fg="white", font=("Arial", 11, "bold"),
    width=15, height=1
).pack(side="left", padx=10)

# View analytics button
tk.Button(
    button_frame, text="View Analytics", command=show_analytics,
    bg="#e67e22", fg="white", font=("Arial", 11, "bold"),
    width=15, height=1
).pack(side="left", padx=10)

# Open folder button
tk.Button(
    button_frame, text="Open Folder", command=show_transaction_folder,
    bg="#3498db", fg="white", font=("Arial", 11, "bold"),
    width=15, height=1
).pack(side="left", padx=10)

# Delete button
tk.Button(
    button_frame, text="Delete Selected", command=delete_transaction,
    bg="#c0392b", fg="white", font=("Arial", 11, "bold"),
    width=15, height=1
).pack(side="left", padx=10)

# Transaction history section
history_frame = tk.Frame(main_frame)
history_frame.pack(expand=True, fill="both", pady=15)

tk.Label(
    history_frame,
    text="TRANSACTION HISTORY",
    font=("Arial", 12, "bold"),
    fg="#0e5cab",
    pady=5
).pack()

tree_container = tk.Frame(history_frame)
tree_container.pack(expand=True, fill="both")

# Treeview para sa transaction history
cols = ("Date", "Description", "Amount")
tree = ttk.Treeview(tree_container, columns=cols, show="headings", height=12)

# Styling ng table
style = ttk.Style()
style.configure("Treeview", font=("Arial", 10), rowheight=25)
style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

tree.column("Date", width=120, anchor="center")
tree.column("Description", width=400, anchor="w")
tree.column("Amount", width=120, anchor="center")  # BINAGO: NAKA-CENTER NA ANG AMOUNT

for col in cols:
    tree.heading(col, text=col, anchor="center")

# Scrollbar for treeview
scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

tree.pack(side="left", fill="both", expand=True)

# Initial display ng transactions
update_display()
cell_entry.focus_set()

# Pinapatakbo ang main application loop
root.mainloop()