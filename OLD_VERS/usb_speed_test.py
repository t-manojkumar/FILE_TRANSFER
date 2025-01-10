import os
import time
import shutil

def measure_speed(source_path, dest_path, file_size_mb=1000):
    """Measure the write and read speed for the USB drive."""
    temp_file = os.path.join(source_path, "temp_test_file.bin")
    
    # Step 1: Create a temporary file for testing
    print(f"Creating a {file_size_mb} MB temporary file...")
    with open(temp_file, "wb") as f:
        f.write(os.urandom(file_size_mb * 1024 * 1024))  # Write random data
    
    # Step 2: Measure write speed (copy to USB)
    start_time = time.time()
    shutil.copy(temp_file, dest_path)
    write_time = time.time() - start_time
    write_speed = file_size_mb / write_time  # MB/s
    
    print(f"Write speed: {write_speed:.2f} MB/s")
    
    # Step 3: Measure read speed (copy back from USB)
    copied_file = os.path.join(dest_path, "temp_test_file.bin")
    start_time = time.time()
    shutil.copy(copied_file, source_path)
    read_time = time.time() - start_time
    read_speed = file_size_mb / read_time  # MB/s
    
    print(f"Read speed: {read_speed:.2f} MB/s")
    
    # Clean up
    os.remove(temp_file)
    os.remove(copied_file)

if __name__ == "__main__":
    source = input("Enter the source path (e.g., C:\\Users\\YourName\\Documents): ")
    dest = input("Enter the USB drive path (e.g., D:\\): ")
    
    if os.path.exists(source) and os.path.exists(dest):
        measure_speed(source, dest)
    else:
        print("Invalid paths. Please check and try again.")
