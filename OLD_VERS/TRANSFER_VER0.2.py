import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

class FileTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Transfer Application")
        self.root.geometry("500x400")
        self.root.configure(bg="#F0F0F0")  # Light gray background

        self.source_path = tk.StringVar()
        self.dest_path = tk.StringVar()

        # Title Label
        title_label = tk.Label(root, text="File Transfer Application", font=("Helvetica", 16, "bold"), bg="#F0F0F0")
        title_label.pack(pady=10)

        # Frame for Source Directory
        source_frame = ttk.Frame(root, padding=10)
        source_frame.pack(fill=tk.X, padx=20, pady=5)

        source_label = ttk.Label(source_frame, text="Source Path:")
        source_label.grid(row=0, column=0, sticky=tk.W, padx=5)

        source_entry = ttk.Entry(source_frame, textvariable=self.source_path, width=40)
        source_entry.grid(row=0, column=1, padx=5)

        source_browse_button = ttk.Button(source_frame, text="Browse", command=self.browse_source)
        source_browse_button.grid(row=0, column=2, padx=5)

        # Frame for Destination Directory
        dest_frame = ttk.Frame(root, padding=10)
        dest_frame.pack(fill=tk.X, padx=20, pady=5)

        dest_label = ttk.Label(dest_frame, text="Destination Path:")
        dest_label.grid(row=0, column=0, sticky=tk.W, padx=5)

        dest_entry = ttk.Entry(dest_frame, textvariable=self.dest_path, width=40)
        dest_entry.grid(row=0, column=1, padx=5)

        dest_browse_button = ttk.Button(dest_frame, text="Browse", command=self.browse_dest)
        dest_browse_button.grid(row=0, column=2, padx=5)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=20)

        # Transfer Button
        self.transfer_button = ttk.Button(root, text="Start Transfer", command=self.start_transfer)
        self.transfer_button.pack(pady=10)

    def browse_source(self):
        """Browse the source folder"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.source_path.set(folder_selected)

    def browse_dest(self):
        """Browse the destination folder"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.dest_path.set(folder_selected)

    def copy_file(self, src, dst):
        """Helper function to copy files with progress"""
        try:
            total_size = os.path.getsize(src)
            bytes_copied = 0
            with open(src, 'rb') as source_file:
                with open(dst, 'wb') as dest_file:
                    while chunk := source_file.read(1024 * 1024):  # 1 MB chunks
                        dest_file.write(chunk)
                        bytes_copied += len(chunk)
                        progress = (bytes_copied / total_size) * 100
                        self.progress_bar['value'] = progress
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

        self.transfer_button.config(state="disabled")
        threading.Thread(target=self.transfer_files, args=(src, dest)).start()

    def transfer_files(self, src, dest):
        """Transfer files and folders"""
        if os.path.isdir(src):
            files_to_transfer = os.listdir(src)
            total_files = len(files_to_transfer)
            for index, file in enumerate(files_to_transfer, 1):
                src_file = os.path.join(src, file)
                dest_file = os.path.join(dest, file)
                success = False
                if os.path.isdir(src_file):
                    os.makedirs(dest_file, exist_ok=True)
                    success = self.transfer_files(src_file, dest_file)
                else:
                    success = self.copy_file(src_file, dest_file)

                if success:
                    self.progress_bar['value'] = (index / total_files) * 100
                    self.root.update_idletasks()

            self.transfer_button.config(state="normal")
            messagebox.showinfo("Success", "Transfer completed successfully.")
        else:
            success = self.copy_file(src, dest)
            self.transfer_button.config(state="normal")
            if success:
                messagebox.showinfo("Success", "Transfer completed successfully.")
            else:
                messagebox.showerror("Error", "File transfer failed.")

# Create the Tkinter root window
root = tk.Tk()

# Instantiate the application
app = FileTransferApp(root)

# Start the Tkinter event loop
root.mainloop()