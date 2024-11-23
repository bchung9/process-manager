import psutil
import tkinter as tk
from tkinter import ttk

def classify_process(cpu_usage, io_usage):
    """Classify a process as CPU-bound or I/O-bound."""
    return "CPU-bound" if cpu_usage > io_usage else "I/O-bound"

def get_process_info():
    """Retrieve information about all active processes."""
    process_info_list = []
    for proc in psutil.process_iter(attrs=['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'io_counters']):
        try:
            p_info = proc.info
            pid = p_info['pid']
            name = p_info['name'] if p_info['name'] is not None else "N/A"
            username = p_info['username'] if p_info['username'] is not None else "N/A"
            cpu_usage = proc.cpu_percent(interval=0.1) or 0.0
            memory_usage = p_info['memory_percent'] or 0.0
            io_counters = proc.io_counters() if proc.io_counters() else None
            io_usage = (io_counters.read_bytes + io_counters.write_bytes) if io_counters else 0
            process_type = "System" if username in ("SYSTEM", "root") else "User"
            bound_type = classify_process(cpu_usage, io_usage)
            process_info_list.append({
                "PID": pid,
                "Name": name,
                "Username": username,
                "Process Type": process_type,
                "CPU Usage (%)": cpu_usage,
                "Memory Usage (%)": memory_usage,
                "I/O Usage (bytes)": io_usage,
                "Bound Type": bound_type
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return process_info_list

def update_table():
    """Fetch latest process information and update the table."""
    for row in tree.get_children():
        tree.delete(row)
    process_info_list = get_process_info()
    for proc in process_info_list:
        tree.insert("", "end", values=(
            proc["PID"], proc["Name"], proc["Username"], proc["Process Type"],
            f"{proc['CPU Usage (%)']:.2f}", f"{proc['Memory Usage (%)']:.2f}",
            proc["I/O Usage (bytes)"], proc["Bound Type"]
        ))

# Create the main application window
root = tk.Tk()
root.title("Process Manager")
root.geometry("800x400")

# Set up the treeview (table)
columns = ("PID", "Name", "Username", "Process Type", "CPU Usage (%)", "Memory Usage (%)", "I/O Usage (bytes)", "Bound Type")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor="center")

# Add a vertical scrollbar to the table
scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")
tree.pack(expand=True, fill="both")

# Add a refresh button
refresh_button = ttk.Button(root, text="Refresh", command=update_table)
refresh_button.pack(pady=5)

# Initialize the table with process information
update_table()

# Run the application
root.mainloop()
