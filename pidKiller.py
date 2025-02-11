import os
import argparse

def createFile(output_dir):
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create full path
    file_path = os.path.join(output_dir, "pids.txt")
    
    fakePids = [1, 2, 3, 4, 5]
    with open(file_path, 'w') as file:
        for pid in fakePids:
            file.write(f"{pid}\n")
    
    print(f"File created in directory: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate PID list')
    parser.add_argument('--directory', type=str, required=True,
                      help='Directory to create pids.txt in')
    args = parser.parse_args()
    
    createFile(args.directory)