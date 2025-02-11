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
                match = re.match(
                    r"\s*(?P<GPU>\d+)\s+(?P<GI_ID>\S+)\s+(?P<CI_ID>\S+)\s+(?P<PID>\d+)\s+(?P<Type>\S+)\s+(?P<Process_Name>.+?)\s+(?P<Memory_Usage>\d+MiB)",
                    line
                )
                if match:
                    pid = match.group("PID")
                    processes[pid] = {
                        "GPU": match.group("GPU"),
                        "GI ID": match.group("GI_ID"),
                        "CI_ID": match.group("CI_ID"),
                        "Type": match.group("Type"),
                        "Process Name": match.group("Process_Name").strip(),
                        "Memory Usage": match.group("Memory_Usage")
                    }

        return processes

    def processes_to_kill(self, process_name_filter=None): # TODO: what to filter? should it be based on mem usage?
        """
        Filters processes to kill based on our criteria.
        
        process_name_filter (optional): don't include these to kill
        
        Return list of PIDs to be killed. 
        """
        pids_to_kill = []
        pids_not_to_kill = []
        
        for pid, info in self.processes.items():
            process_name = info["Process Name"]

            if process_name_filter and any(proc in process_name for proc in process_name_filter):
                pids_not_to_kill.append(pid)
                continue  # skip if don't wanna kill process

            pids_to_kill.append(pid)

        print(f"pids to kill: {pids_to_kill}")
        print(f"pids not to kill: {pids_not_to_kill}")
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
    # gpu_manager.kill_processes(pids_to_terminate)
        
# call this Python file from an API in the backend
