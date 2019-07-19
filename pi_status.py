import subprocess

def run_shell_cmd(cmd):
    # TODO: for multiple arguments parse cmd and pass different parts to run
    # cmd.split(' ')
    return subprocess.run([cmd], stdout=subprocess.PIPE).stdout.decode('utf-8')

def get_status():
    uptime_out = run_shell_cmd('uptime')
    ifconfig_out = subprocess.run(['ifconfig', 'eth0'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    st_out = run_shell_cmd('speedtest')
    python_out = subprocess.run(['pgrep', '-a', 'python'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    ltl_out = run_shell_cmd('/home/pi/castes-scripts/ltl.sh')
    cpu_gpu_temps_out = run_shell_cmd('/home/pi/castes-scripts/check_cpu_gpu_temps.sh')
    return "Uptime:\n" + uptime_out + \
         "\n\n" + cpu_gpu_temps_out + \
         "\n\nSpeedtest:\n" + st_out + \
         "\n\nNetwork status:\n" + ifconfig_out + \
         "\n\nPython running:\n" + python_out + \
         "\n\nTwitter bot:\n" + ltl_out

def get_uptime():
    uptime_out = run_shell_cmd('uptime')
    free_h_out = subprocess.run(["free","-h"], stdout=subprocess.PIPE).stdout.decode('utf-8')
    return "Uptime:\n" + uptime_out + "\nMemory:\n" + free_h_out

def get_cpu_gpu_temps():
    return run_shell_cmd('/home/pi/castes-scripts/check_cpu_gpu_temps.sh')

def get_ifconfig():
    ifconfig_out = subprocess.run(['ifconfig', 'eth0'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    return "Network status:\n" + ifconfig_out

def get_speedtest():
    st_out = run_shell_cmd('speedtest')
    return "Speedtest:\n" + st_out

def get_ppy():
    python_out = subprocess.run(['pgrep', '-a', 'python'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    return "Python running:\n" + python_out

def get_ltl():
    ltl_out = run_shell_cmd('/home/pi/castes-scripts/ltl.sh')
    return "Twitter bot:\n" + ltl_out

def get_log_tail():
    return subprocess.run(['/home/pi/castes-scripts/telegram-bot/tail.sh'], stdout=subprocess.PIPE).stdout.decode('utf-8')

def fortune():
    return subprocess.run(['fortune'], stdout=subprocess.PIPE).stdout.decode('utf-8')

def get_lasdl():
    lasdl_out = run_shell_cmd('/home/pi/castes-scripts/lasdl.sh')
    return lasdl_out

def sudo_apt_update():
    with subprocess.Popen(["sudo", "apt", "update"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        process.wait(60)
        out = "stdout:\n" + process.stdout.read().decode("ascii") + "\nstderr:\n" + process.stderr.read().decode("ascii")
    return out

def apt_list_upgradable():
    with subprocess.Popen(["apt", "list", "-u"], shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        process.wait(60)
        out = "stdout:\n" + process.stdout.read().decode("ascii") + "\nstderr:\n" + process.stderr.read().decode("ascii")
    return out

def sudo_apt_upgrade():
    with subprocess.Popen(["sudo", "apt", "upgrade", "-y"], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        process.wait(600)
        out = "stdout:\n" + process.stdout.read().decode("ascii") + "\nstderr:\n" + process.stderr.read().decode("ascii")
    return out