import subprocess

def run_shell_cmd(cmd):
    # for multiple arguments parse cmd and pass different parts to run
    # cmd.split(' ')
    return subprocess.run([cmd], stdout=subprocess.PIPE).stdout.decode('utf-8')

def get_status():
    uptime_out = run_shell_cmd('uptime')
    ifconfig_out = subprocess.run(['ifconfig', 'eth0'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    st_out = run_shell_cmd('speedtest')
    python_out = subprocess.run(['pgrep', '-a', 'python'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    ltl_out = run_shell_cmd('/home/pi/castes-scripts/ltl.sh')
    return "Uptime:\n" + uptime_out + \
         "\n\nSpeedtest:\n" + st_out + \
         "\n\nNetwork status:\n" + ifconfig_out + \
         "\n\nPython running:\n" + python_out + \
         "\n\nTwitter bot:\n" + ltl_out

def get_uptime():
    uptime_out = run_shell_cmd('uptime')
    return "Uptime:\n" + uptime_out

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