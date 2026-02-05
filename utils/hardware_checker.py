import platform
import psutil
import GPUtil
import os
from typing import Dict, Union

def get_system_info() -> Dict[str, Union[str, float]]:
    """Get comprehensive system hardware information.
    
    Returns:
        Dictionary containing OS, CPU, RAM, GPU, VRAM, and Storage information
    """
    # GPU Detection
    try:
        gpus = GPUtil.getGPUs()
        gpu_name = gpus[0].name if gpus else "No GPU Detected"
        gpu_vram = gpus[0].memoryTotal if gpus else 0
    except Exception:
        gpu_name, gpu_vram = "No GPU Detected", 0

    # CPU Detection
    try:
        cpu = platform.processor()
        if not cpu or cpu.strip() == "":
            # Fallback for systems where processor() returns empty string
            import cpuinfo
            cpu = cpuinfo.get_cpu_info().get('brand_raw', 'Unknown CPU')
    except Exception:
        cpu = "Unknown CPU"

    # Storage Detection (cross-platform)
    try:
        # Use the drive where the script is located
        if platform.system() == "Windows":
            # Get the drive letter of the current directory
            disk_path = os.path.splitdrive(os.getcwd())[0] + os.sep
        else:
            disk_path = '/'
        storage_gb = round(psutil.disk_usage(disk_path).total / (1024**3), 2)
    except Exception:
        storage_gb = 0

    # RAM Detection
    try:
        ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    except Exception:
        ram_gb = 0

    info = {
        "OS": f"{platform.system()} {platform.release()}",
        "CPU": cpu,
        "RAM (GB)": ram_gb,
        "GPU": gpu_name,
        "VRAM (GB)": round(gpu_vram, 2),
        "Storage (GB)": storage_gb
    }
    return info
