import subprocess
from robbamia import raspi_script_dir

def run_shell_cmd(cmd: str) -> str:
    cmd = cmd.strip().replace('  ', ' ').split(' ')  # is now a list of strings
    return subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')


def get_status():
    uptime_out = run_shell_cmd('uptime')
    ifconfig_out = run_shell_cmd("ifconfig eth0")
    st_out = run_shell_cmd('speedtest')
    python_out = run_shell_cmd("pgrep -a python")
    ltl_out = run_shell_cmd(raspi_script_dir + 'ltl.sh')
    cpu_gpu_temps_out = run_shell_cmd(raspi_script_dir + 'check_cpu_gpu_temps.sh')
    return "Uptime:\n" + uptime_out + \
         "\n\n" + cpu_gpu_temps_out + \
         "\n\nSpeedtest:\n" + st_out + \
         "\n\nNetwork status:\n" + ifconfig_out + \
         "\n\nPython running:\n" + python_out + \
         "\n\nTwitter bot:\n" + ltl_out

def get_uptime():
    uptime_out = run_shell_cmd('uptime')
    free_h_out = run_shell_cmd("free -h")
    df_h_root_out = run_shell_cmd("df -h /")
    return uptime_out + "\n\n" + free_h_out + "\n\n" + df_h_root_out

def get_cpu_gpu_temps():
    return run_shell_cmd(raspi_script_dir + 'check_cpu_gpu_temps.sh')

def get_ifconfig():
    ifconfig_out = run_shell_cmd("ifconfig eth0")
    return "Network status:\n" + ifconfig_out

def get_speedtest():
    st_out = run_shell_cmd('speedtest')
    return "Speedtest:\n" + st_out

def get_ppy():
    python_out = run_shell_cmd("pgrep -a python")
    return "Python running:\n" + python_out

def get_ltl():
    ltl_out = run_shell_cmd(raspi_script_dir + 'ltl.sh')
    return "Twitter bot:\n" + ltl_out

def get_log_tail():
    return run_shell_cmd('cd ' + raspi_script_dir + 'telegram-bot/logs && tail -10 "$(ls | tail -1)" && cd -')

def fortune():
    return run_shell_cmd("fortune")

def get_lasdl():
    lasdl_out = run_shell_cmd(raspi_script_dir + 'lasdl.sh')
    return lasdl_out

def sudo_apt_update():
    with subprocess.Popen(["sudo", "apt-get", "update"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        process.wait(60)
        out = "stdout:\n" + process.stdout.read().decode("ascii") + "\nstderr:\n" + process.stderr.read().decode("ascii")
    return out

def apt_list_upgradable():
    with subprocess.Popen(["apt", "list", "-u"], shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        process.wait(60)
        out = "stdout:\n" + process.stdout.read().decode("ascii") + "\nstderr:\n" + process.stderr.read().decode("ascii")
    return out

def sudo_apt_upgrade():
    with subprocess.Popen(["sudo", "apt-get", "upgrade", "-y"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        process.wait(600)
        out = "stdout:\n" + process.stdout.read().decode("ascii") + "\nstderr:\n" + process.stderr.read().decode("ascii")
    return out

def get_disk_usage():
    return run_shell_cmd("df -h /")
