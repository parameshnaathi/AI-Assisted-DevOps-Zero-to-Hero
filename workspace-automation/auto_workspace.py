import os
import subprocess
from pathlib import Path

REPO_NAME = "vm-health-monitor"

SCRIPT_CONTENT = '''#!/bin/bash

EXPLAIN=false

if [[ "$1" == "explain" ]]; then
    EXPLAIN=true
fi

CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8}')
MEMORY=$(free | awk '/Mem:/ {printf("%.0f"), $3/$2 * 100}')
DISK=$(df / | awk 'END{print $5}' | sed 's/%//')

HEALTHY=true
REASON=""

if (( $(echo "$CPU > 60" | bc -l) )); then
    HEALTHY=false
    REASON+="CPU usage high ($CPU%). "
fi

if [ "$MEMORY" -gt 60 ]; then
    HEALTHY=false
    REASON+="Memory usage high ($MEMORY%). "
fi

if [ "$DISK" -gt 60 ]; then
    HEALTHY=false
    REASON+="Disk usage high ($DISK%). "
fi

if [ "$HEALTHY" = true ]; then
    STATUS="Healthy"
else
    STATUS="Not Healthy"
fi

echo "VM Health Status: $STATUS"

if [ "$EXPLAIN" = true ]; then
    echo "Reason: ${REASON:-All metrics within threshold}"
fi
'''

README = '''
# VM Health Monitor

Checks:
- CPU utilization
- Memory utilization
- Disk utilization

Threshold:
- Healthy < 60%
- Not Healthy > 60%

Usage:

./health_check.sh

./health_check.sh explain
'''

def run_command(command):
    print(f"\nRunning: {' '.join(command)}")

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        shell=True
    )

    print(result.stdout)

    if result.stderr:
        print("ERROR:")
        print(result.stderr)

    return result.returncode

# Create project directory
project_path = Path(REPO_NAME)

if not project_path.exists():
    project_path.mkdir()
    print(f"Created directory: {REPO_NAME}")

# Create shell script
script_path = project_path / "health_check.sh"

with open(script_path, "w") as f:
    f.write(SCRIPT_CONTENT)

# Create README
readme_path = project_path / "README.md"

with open(readme_path, "w") as f:
    f.write(README)

print("Files generated successfully.")

# Move into project folder
os.chdir(REPO_NAME)

# Initialize git
run_command(["git", "init"])

# Set branch to main
run_command(["git", "branch", "-M", "main"])

# Create GitHub repo
run_command([
    "gh",
    "repo",
    "create",
    REPO_NAME,
    "--public",
    "--source=.",
    "--remote=origin"
])

# Git add
run_command(["git", "add", "."])

# Git commit
run_command([
    "git",
    "commit",
    "-m",
    "Initial commit"
])

# Push code
run_command([
    "git",
    "push",
    "-u",
    "origin",
    "main"
])

print("\nSUCCESS: Repository created and code pushed.")