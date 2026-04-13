import paramiko, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

host = "223.109.49.160"
port = 22
user = "root"
password = "BEZAeGg:"

def run(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout, get_pty=True)
    return stdout.read().decode('utf-8', errors='replace').strip()

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port=port, username=user, password=password,
                timeout=15, look_for_keys=False, allow_agent=False)

    # Check what models the gateway sees
    print(run(ssh, """curl -s 'http://127.0.0.1:18789/api/v1/models' \
      -H 'Authorization: Bearer 4151c5a0d8807ba335a84940b38e3d8b8737930e0b3054cc' 2>&1 | head -c 3000"""))

    ssh.close()
except Exception as e:
    print(f"Error: {e}")