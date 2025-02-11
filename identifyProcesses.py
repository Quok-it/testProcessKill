import subprocess

def get_gpu_processes():
    """
    Parse output of nvidia-smi and store GPU processes in dict.
    Dictionary uses PIDs as keys and stores all other process info as values .
    """

    # nvidia-smi command
    sp = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # convert output to list of lines
    lines = sp.stdout.split("\n")

    process_section = False
    processes = {}

    for line in lines:
        line = line.strip()
        
        # start of processes section
        if "Processes:" in line:
            process_section = True
            continue

        # skip table headers
        if process_section and ("===" in line or "GPU   GI   CI" in line):
            continue

        # get process info
        if process_section and line:
            parts = line.split()
            if len(parts) >= 6:
                pid = parts[4]  # PID at index 4
                process_info = {
                    "GPU": parts[0],
                    "Type": parts[5],
                    "Process Name": " ".join(parts[6:]),
                    "Memory Usage": parts[-2] + " " + parts[-1]
                }
                processes[pid] = process_info

    return processes

if __name__ == "__main__":
    gpu_processes = get_gpu_processes()
    
    # print process dictionary (for debugging)
    for pid, info in gpu_processes.items():
        print(f"PID: {pid} -> {info}")

    # # Save to a file (PIDs separated by commas)
    # with open("gpu_pids.txt", "w") as f:
    #     f.write(",".join(gpu_processes.keys()))
