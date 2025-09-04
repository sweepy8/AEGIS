# test bench can delete

import os, time

last_cpu_util = 0.0

def get_cpu_util() -> float:
    non_idle = 0.0
    # Get CPU utilization information
    with open('/proc/stat') as f:
        for line in f:
            if line.startswith('cpu '):
                print(line)
                parts = line.split()
                user, nice, system, idle, iowait, irq, softirq, steal = map(float, parts[1:9])
                idle_all  = idle + iowait
                non_idle  = user + nice + system + irq + softirq + steal

    curr_util = (non_idle / (idle_all + non_idle))        # type: ignore
    
    last_cpu_util = curr_util                                # type: ignore
    return curr_util


while True:

    # POPULATE RASPBERRY PI TELEMETRY
    cpu_util_pct: list[str] = get_cpu_util()    # type: ignore
    adc_vals: list[str] = os.popen('vcgencmd pmic_read_adc').read().split()
    fmt = lambda idx, pre, post: round(
        float(adc_vals[idx].replace(pre,'').replace(post,'')), 4)
    vdd_core_a: float = fmt(13, 'current(6)=', 'A')
    vdd_core_v: float = fmt(49, 'volt(24)=', 'V')

    mem: list[str] = os.popen('free').read().split()[7:9]
    mem_util_pct: float = round(100*int(mem[1])/int(mem[0]), 2)

    storage_avail_str: str = os.popen('df -h /').read().split()[10]
    if storage_avail_str.find('G') >= 0:
        storage_avail_gb = float(storage_avail_str[:-1])
    elif storage_avail_str.find('M') >= 0:
        storage_avail_gb = float(storage_avail_str[:-1]) / 1000
    else:
        storage_avail_gb = 0.0

    uptime: str = os.popen("awk '{print $1}' /proc/uptime").read(
                            ).replace('\n', '')
    uptime_s: float = round(float(uptime))

    soc_temp_c: float = float(os.popen('vcgencmd measure_temp').read()
                            .replace('temp=','').replace("'C\n", ''))



    print(storage_avail_gb)
    print(cpu_util_pct)
    time.sleep(.5)