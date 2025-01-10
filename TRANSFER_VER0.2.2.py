import os
import shutil
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

class FileTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Transfer Application")
        self.root.geometry("600x500")
        self.root.configure(bg="#F0F0F0")

        self.source_path = tk.StringVar()
        self.dest_path = tk.StringVar()
        self.select_all = tk.BooleanVar()
        self.cancel_transfer = False

        # Title Label
        title_label = tk.Label(root, text="File Transfer Application", font=("Helvetica", 16, "bold"), bg="#F0F0F0")
        title_label.pack(pady=10)

        # Source Frame
        source_frame = ttk.Frame(root, padding=10)
        source_frame.pack(fill=tk.X, padx=20, pady=5)

        source_label = ttk.Label(source_frame, text="Source Path:")
        source_label.grid(row=0, column=0, sticky=tk.W, padx=5)

        source_entry = ttk.Entry(source_frame, textvariable=self.source_path, width=40)
        source_entry.grid(row=0, column=1, padx=5)

        source_browse_button = ttk.Button(source_frame, text="Browse", command=self.browse_source)
        source_browse_button.grid(row=0, column=2, padx=5)

        # Destination Frame
        dest_frame = ttk.Frame(root, padding=10)
        dest_frame.pack(fill=tk.X, padx=20, pady=5)

        dest_label = ttk.Label(dest_frame, text="Destination Path:")
        dest_label.grid(row=0, column=0, sticky=tk.W, padx=5)

        dest_entry = ttk.Entry(dest_frame, textvariable=self.dest_path, width=40)
        dest_entry.grid(row=0, column=1, padx=5)

        dest_browse_button = ttk.Button(dest_frame, text="Browse", command=self.browse_dest)
        dest_browse_button.grid(row=0, column=2, padx=5)

        # Select All Checkbox
        select_all_check = ttk.Checkbutton(root, text="Select All Files", variable=self.select_all)
        select_all_check.pack(pady=5)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=10)

        # Transfer Status Frame
        status_frame = ttk.Frame(root)
        status_frame.pack(pady=10)

        self.current_file_label = ttk.Label(status_frame, text="Currently Transferring: N/A", width=50)
        self.current_file_label.grid(row=0, column=0, padx=5)

        self.speed_label = ttk.Label(status_frame, text="Speed: 0 MB/s", width=20)
        self.speed_label.grid(row=0, column=1, padx=5)

        self.time_remaining_label = ttk.Label(status_frame, text="ETR: N/A")
        self.time_remaining_label.grid(row=1, column=0, columnspan=2)

        # Transfer and Cancel Buttons
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)

        self.transfer_button = ttk.Button(button_frame, text="Start Transfer", command=self.start_transfer)
        self.transfer_button.grid(row=0, column=0, padx=5)

        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel_transfer_action, state="disabled")
        self.cancel_button.grid(row=0, column=1, padx=5)

    def browse_source(self):
        """Browse and select multiple files"""
        files_selected = filedialog.askopenfilenames(title="Select Files")
        if files_selected:
            self.source_path.set(";".join(files_selected))  # Join file paths with semicolon for display


    def browse_dest(self):
        """Browse the destination folder"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.dest_path.set(folder_selected)

    def cancel_transfer_action(self):
        """Cancel the ongoing transfer"""
        self.cancel_transfer = True
        self.cancel_button.config(state="disabled")
        self.transfer_button.config(state="normal")
        messagebox.showinfo("Cancelled", "Transfer has been cancelled.")

    def copy_file(self, src, dst):
        """Helper function to copy files with progress, transfer speed, and time estimation"""
        try:
            total_size = os.path.getsize(src)
            bytes_copied = 0
            start_time = time.time()

            with open(src, 'rb') as source_file:
                with open(dst, 'wb') as dest_file:
                    while chunk := source_file.read(1024 * 1024):  # 1 MB chunks
                        if self.cancel_transfer:
                            return False  # Exit if transfer is cancelled

                        dest_file.write(chunk)
                        bytes_copied += len(chunk)
                        elapsed_time = time.time() - start_time
                        speed = bytes_copied / elapsed_time / (1024 * 1024)  # MB/s
                        progress = (bytes_copied / total_size) * 100
                        self.progress_bar['value'] = progress

                        # Update labels
                        self.speed_label.config(text=f"Speed: {speed:.2f} MB/s")
                        time_remaining = (total_size - bytes_copied) / (bytes_copied / elapsed_time) if bytes_copied > 0 else 0
                        self.time_remaining_label.config(
                            text=f"ETR: {int(time_remaining)} sec ({time_remaining // 60:.0f} min)"
                        )

                        self.root.update_idletasks()

            return True
        except Exception as e:
            print(f"Error copying {src} to {dst}: {e}")
            return False

    def start_transfer(self):
        """Start file transfer in a separate thread"""
        src = self.source_path.get()
        dest = self.dest_path.get()

        if not src:
            messagebox.showerror("Error", "Please select a source path.")
            return
        if not dest:
            messagebox.showerror("Error", "Please select a destination path.")
            return

        self.cancel_transfer = False
        self.transfer_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        threading.Thread(target=self.transfer_files, args=(src, dest)).start()

    def transfer_files(self, src, dest):
        """Transfer files and folders"""
        if os.path.isdir(src):
            files_to_transfer = os.listdir(src)
            total_files = len(files_to_transfer)

            total_bytes = sum(os.path.getsize(os.path.join(src, f)) for f in files_to_transfer)
            bytes_transferred = 0
            start_time = time.time()

            for index, file in enumerate(files_to_transfer, 1):
                if self.cancel_transfer:
                    break

                src_file = os.path.join(src, file)
                dest_file = os.path.join(dest, file)
                self.current_file_label.config(text=f"Currently Transferring: {file}")

                if os.path.isdir(src_file):
                    os.makedirs(dest_file, exist_ok=True)
                    self.transfer_files(src_file, dest_file)
                else:
                    success = self.copy_file(src_file, dest_file)
                    if success:
                        bytes_transferred += os.path.getsize(src_file)
                        overall_progress = (bytes_transferred / total_bytes) * 100
                        self.progress_bar['value'] = overall_progress

            self.transfer_button.config(state="normal")
            self.cancel_button.config(state="disabled")
            if not self.cancel_transfer:
                messagebox.showinfo("Success", "Transfer completed successfully.")
        else:
            success = self.copy_file(src, dest)
            self.transfer_button.config(state="normal")
            self.cancel_button.config(state="disabled")
            if success and not self.cancel_transfer:
                messagebox.showinfo("Success", "Transfer completed successfully.")
            elif self.cancel_transfer:
                messagebox.showinfo("Cancelled", "Transfer was cancelled.")

# Create the Tkinter root window
root = tk.Tk()

# Instantiate the application
app = FileTransferApp(root)

# Start the Tkinter event loop
root.mainloop()
