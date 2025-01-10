import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess

class FileTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Transfer Application")
        self.root.geometry("500x400")
        
        self.source_path = tk.StringVar()
        self.dest_path = tk.StringVar()

        # Source Directory
        self.source_label = tk.Label(root, text="Source Path:")
        self.source_label.pack(pady=10)

        self.source_entry = tk.Entry(root, textvariable=self.source_path, width=40)
        self.source_entry.pack(pady=5)

        self.source_browse_button = tk.Button(root, text="Browse", command=self.browse_source)
        self.source_browse_button.pack(pady=5)

        # Destination Directory
        self.dest_label = tk.Label(root, text="Destination Path:")
        self.dest_label.pack(pady=10)

        self.dest_entry = tk.Entry(root, textvariable=self.dest_path, width=40)
        self.dest_entry.pack(pady=5)

        self.dest_browse_button = tk.Button(root, text="Browse", command=self.browse_dest)
        self.dest_browse_button.pack(pady=5)

        # Mobile Device Support
        self.mobile_check = tk.Checkbutton(root, text="Transfer to Mobile (via ADB)", command=self.toggle_mobile)
        self.mobile_check.pack(pady=10)

        self.is_mobile = False

        # Progress Bar
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=20)

        # Transfer Button
        self.transfer_button = tk.Button(root, text="Start Transfer", command=self.start_transfer)
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

    def toggle_mobile(self):
        """Toggle the mobile transfer mode"""
        self.is_mobile = not self.is_mobile
        if self.is_mobile:
            self.dest_path.set('')  # Clear destination path if mobile mode is enabled
            self.dest_entry.config(state="disabled")  # Disable destination field
        else:
            self.dest_entry.config(state="normal")  # Enable destination field

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

    def transfer_to_mobile(self, src, dest):
        """Transfer files to mobile via ADB"""
        try:
            command = f"adb push \"{src}\" \"/sdcard/{dest}\""
            subprocess.run(command, shell=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error transferring to mobile: {e}")
            return False

    def transfer_from_mobile(self, src, dest):
        """Transfer files from mobile to PC via ADB"""
        try:
            command = f"adb pull \"/sdcard/{src}\" \"{dest}\""
            subprocess.run(command, shell=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error transferring from mobile: {e}")
            return False

    def start_transfer(self):
        """Start file transfer in a separate thread"""
        src = self.source_path.get()
        dest = self.dest_path.get()

        if not src:
            messagebox.showerror("Error", "Please select a source path.")
            return

        if self.is_mobile:
            if not dest:
                messagebox.showerror("Error", "Please select the mobile transfer mode.")
                return
            # Start transfer to/from mobile device
            self.transfer_button.config(state="disabled")
            threading.Thread(target=self.transfer_mobile_files, args=(src, dest)).start()
        else:
            if not dest:
                messagebox.showerror("Error", "Please select a destination path.")
                return
            # Start file transfer
            self.transfer_button.config(state="disabled")
            threading.Thread(target=self.transfer_files, args=(src, dest)).start()

    def transfer_files(self, src, dest):
        """Transfer files and folders"""
        if os.path.isdir(src):
            # Copy directories recursively
            files_to_transfer = os.listdir(src)
            total_files = len(files_to_transfer)
            for index, file in enumerate(files_to_transfer, 1):
                src_file = os.path.join(src, file)
                dest_file = os.path.join(dest, file)
                success = False
                if os.path.isdir(src_file):
                    # Create subfolder in destination
                    os.makedirs(dest_file, exist_ok=True)
                    success = self.transfer_files(src_file, dest_file)
                else:
                    success = self.copy_file(src_file, dest_file)

                # Check success and update progress
                if success:
                    self.progress_bar['value'] = (index / total_files) * 100
                    self.root.update_idletasks()

            self.transfer_button.config(state="normal")
            messagebox.showinfo("Success", "Transfer completed successfully.")
        else:
            # Copy single file
            success = self.copy_file(src, dest)
            self.transfer_button.config(state="normal")
            if success:
                messagebox.showinfo("Success", "Transfer completed successfully.")
            else:
                messagebox.showerror("Error", "File transfer failed.")

    def transfer_mobile_files(self, src, dest):
        """Transfer files to/from mobile"""
        files_to_transfer = os.listdir(src)
        total_files = len(files_to_transfer)

        for index, file in enumerate(files_to_transfer, 1):
            src_file = os.path.join(src, file)
            success = False
            if self.is_mobile:
                success = self.transfer_to_mobile(src_file, file)  # Transfer to mobile
            else:
                success = self.transfer_from_mobile(file, dest)  # Transfer from mobile

            # Update progress
            if success:
                self.progress_bar['value'] = (index / total_files) * 100
                self.root.update_idletasks()

        self.transfer_button.config(state="normal")
        messagebox.showinfo("Success", "Mobile transfer completed successfully.")

# Create the Tkinter root window
root = tk.Tk()

# Instantiate the application
app = FileTransferApp(root)

# Start the Tkinter event loop
root.mainloop()
