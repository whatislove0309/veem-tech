import os
import argparse
import time
import logging
import shutil
import filecmp

def log_action(action, path):
    logging.info(f"{action}: {path}")
    
def copy_file(source_path, replica_path):
    shutil.copy2(source_path, replica_path)
    log_action("Copied", replica_path)

def delete_file(path):
    os.remove(path)
    log_action("Deleted", path)

def delete_dir(path):
    shutil.rmtree(path)
    log_action("Deleted directory", path)

def sync_folders(source_dir, destination_dir):
    # Ensure source directory exists
    if (not os.path.exists(source_dir)):
        logging.error("Source directory does not exist")
        return False
    
    # Ensure destination directory exists
    if (not os.path.exists(destination_dir)):
        os.mkdir(destination_dir)
        log_action("Created directory: ", destination_dir)
        
    logging.info(f"Synchronizing {source_dir} to {destination_dir}")
    
    # Get items from both directories
    source_items = set(os.listdir(source_dir))
    destination_items = set(os.listdir(destination_dir))
    
    for item in source_items:
        source_item = os.path.join(source_dir, item)
        dest_item = os.path.join(destination_dir, item)
        
        # If item is directory call recursive function
        if (os.path.isdir(source_item)):
            sync_folders(source_item, dest_item)
        # If item is file copy to destination directory
        else:
            if (not os.path.exists(dest_item) or not filecmp.cmp(source_item, dest_item, shallow=False)):
                copy_file(source_item, dest_item)
    
    # Remove items from destination directory that are not in source 
    for item in destination_items - source_items:
        dest_item = os.path.join(destination_dir, item)
        
        if (os.path.isdir(dest_item)):
            delete_dir(dest_item)
        else:
            delete_file(dest_item) 
    
    return True
    
def setup_logging(dir):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(dir),
            logging.StreamHandler()
        ]
    )
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("interval", type=int)

    args = parser.parse_args()
    
    logging_dir = "logs/sync.logs"        
    setup_logging(logging_dir)
    
    logging.info(f"Source: {args.source}")
    logging.info(f"Destination: {args.destination}")
    logging.info(f"Interval: {args.interval}\n")
    
    try:
        while True:
            if (sync_folders(args.source, args.destination)):
                time.sleep(args.interval)
            else:
                break
    except KeyboardInterrupt:
        logging.info("Synchronisation interrupted by user.")
    
if __name__ == "__main__":
    main()