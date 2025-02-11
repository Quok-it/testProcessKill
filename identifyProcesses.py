""" 
Parse output of nvidia-smi into a python dictionary.
"""

import subprocess

def get_gpu_processes():

    # run nvidia-smi
    sp = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # convert output to list of lines
    lines = sp.stdout.split("\n")

    process_section = False
    processes = []

    for line in lines:
        line = line.strip()
        
        # detect processes header
        if "Processes:" in line:
            process_section = True
            continue

        # skip table header
        if process_section and "===" in line:
            continue

        # get process info
        if process_section and line:
            processes.append(line)

    return processes

if __name__ == "__main__":
    gpu_processes = get_gpu_processes()
    for process in gpu_processes:
        print(process)
        
# txt file with PIDs separated by commas