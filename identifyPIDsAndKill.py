import subprocess
import re
import os

class GPUProcessManager:
    """
    This class lists, filters gpus to kill, and kills these processes
    """
    
    def __init__(self):
        self.processes = self.get_gpu_processes()

    def get_gpu_processes(self):
        """
        Parse output of nvidia-smi and store GPU processes in dict.
        Dictionary uses PIDs as keys and stores all other process info as values.
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
            if process_section and ("===" in line or "+" in line or "GPU   GI   CI" in line):
                continue

            # get process info
            if process_section and line:
                parts = line.split()
                if len(parts) >= 6:
                    pid = parts[4]  # PID at index 4 (key)
                    process_info = {
                        "GPU": parts[1],
                        "GI ID": parts[2],
                        "CI ID": parts[3],
                        "Type": parts[5],
                        "Process Name": " ".join(parts[6:-2]),
                        "Memory Usage": parts[-2]
                    }
                    processes[pid] = process_info

        return processes

    def processes_to_kill(self, process_name_filter=None, memory_threshold=None):  
        """
        filter processes to kill based on:
        - process_name_filter: Don't kill if name contains any of these substrings
        - memory_threshold: Don't kill if memory usage is below this threshold (in MiB)

        return list of PIDs to be killed.
        """

        pids_to_kill = []
        pids_not_to_kill = []
        
        for pid, info in self.processes.items():
            process_name = info["Process Name"]
            memory_usage_str = info["Memory Usage"]

            # convert memory usage to int (remove "MiB" and convert)
            memory_usage = int(memory_usage_str.replace("MiB", "").strip())

            # don't kill these processes
            if process_name_filter and any(proc in process_name for proc in process_name_filter):
                pids_not_to_kill.append(pid)
                continue 
            
            if memory_threshold is not None and memory_usage < memory_threshold:
                pids_not_to_kill.append(pid)
                continue 

            # else add to kill list
            pids_to_kill.append(pid)

        print(f"PIDs to kill: {pids_to_kill}")
        print(f"PIDs NOT to kill: {pids_not_to_kill}")
        
        return pids_to_kill

    def kill_processes(self, pids_to_kill): 
        """
        Kill all processes that have been flagged using `sudo kill -9 <PID>`.
        """
        if not pids_to_kill:
            print("No processes to kill.")
            return
        
        for pid in pids_to_kill:
            try:
                subprocess.run(["sudo", "kill", "-9", pid], check=True)
                print(f"Killed process with PID {pid}")
            except Exception as e:
                print(f"Uh oh, error killing PID {pid}")
                
        # save killed PIDs to a file
        # save to file (PIDs separated by commas) --> maybe this can be sent back to the user informing them of the processes killed
        with open("killed_gpu_pids.txt", "w") as f:
            f.write("\n".join(pids_to_kill))

if __name__ == "__main__":
    gpu_manager = GPUProcessManager()
        
    # print process dictionary (for debugging)
    for pid, info in gpu_manager.processes.items():
        print(f"PID: {pid} -> {info}")

    # define filter conditions
    process_name_filter = ["Xorg", "gnome-shell"]

    # Get processes to kill
    pids_to_terminate = gpu_manager.processes_to_kill(process_name_filter=process_name_filter)

    # Kill processes
    gpu_manager.kill_processes(pids_to_terminate)
        
# call this Python file from an API in the backend
