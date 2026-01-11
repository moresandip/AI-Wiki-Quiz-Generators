import subprocess
import os

def run_git_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return f"Command: {command}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nReturn Code: {result.returncode}\n" + "-"*20 + "\n"
    except Exception as e:
        return f"Error running {command}: {e}\n" + "-"*20 + "\n"

commands = [
    "git status",
    "git remote -v",
    "git branch -vv",
    "git log -1",
    "git diff --stat"
]

output = ""
for cmd in commands:
    output += run_git_command(cmd)

with open("git_debug_output.txt", "w", encoding="utf-8") as f:
    f.write(output)

print("Git debug info written to git_debug_output.txt")
