#!/usr/bin/env python3
"""
Fixer CLI - A comprehensive development tool for fixing issues and maintaining code quality.
"""

import json
import os
import signal
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import git
import typer
from git import Repo
from typer import Argument, Option

app = typer.Typer(
    name="fixer",
    help="A comprehensive CLI tool for fixing issues and maintaining code quality",
    add_completion=False,
)

# Global configuration
FIX_LOG_FILE = "FIX_LOG.md"
DIAGNOSTIC_SCRIPT = "diagnostic_script.py"


def log_fix_result(
    status: str,
    tag: str,
    files_modified: List[str],
    summary: str,
    test_result: str,
    notes: Optional[str] = None,
) -> None:
    """Log fix results to FIX_LOG.md"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"""
## Fix Entry - {timestamp}

- ✅ **Status**: {status}
- 🕒 **Timestamp**: {timestamp}
- 🏷️ **Tag**: {tag}
- 📄 **Files Modified**: {', '.join(files_modified) if files_modified else 'None'}
- 🧩 **Summary**: {summary}
- 🔍 **Test Result**: {test_result}
- 💬 **Notes**: {notes or 'None'}

---
"""

    # Create or append to FIX_LOG.md
    with open(FIX_LOG_FILE, "a") as f:
        f.write(log_entry)

    typer.echo(f"✅ Fix logged to {FIX_LOG_FILE}")


def get_git_repo() -> Optional[Repo]:
    """Get git repository object"""
    try:
        return Repo(".")
    except git.InvalidGitRepositoryError:
        return None


def get_staged_files() -> List[str]:
    """Get list of staged files"""
    repo = get_git_repo()
    if not repo:
        return []

    staged_files = []
    for item in repo.index.diff("HEAD"):
        staged_files.append(item.a_path)

    return staged_files


def run_command(
    cmd: List[str], capture_output: bool = True
) -> subprocess.CompletedProcess:
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            cmd, capture_output=capture_output, text=True, check=False
        )
        return result
    except Exception as e:
        typer.echo(f"❌ Error running command {' '.join(cmd)}: {e}")
        return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr=str(e))


def kill_processes_on_port(port: int) -> bool:
    """Kill all processes using the specified port"""
    try:
        # Find processes using the port - try multiple approaches
        result = run_command(["lsof", "-ti", str(port)])
        
        # If lsof -ti fails, try lsof -i with parsing
        if result.returncode != 0 or not result.stdout.strip():
            # Try alternative approach
            result = run_command(["lsof", "-i", f":{port}"])
            if result.returncode != 0 or not result.stdout.strip():
                typer.echo(f"ℹ️  No processes found using port {port}")
                return True
            
            # Parse the output to extract PIDs
            lines = result.stdout.strip().split('\n')
            pids = []
            for line in lines:
                if line.strip() and not line.startswith('COMMAND'):
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            pid = int(parts[1])
                            pids.append(pid)
                        except (ValueError, IndexError):
                            continue
        else:
            # Parse PIDs from lsof -ti output
            pids = []
            for pid_str in result.stdout.strip().split('\n'):
                if pid_str.strip():
                    try:
                        pid = int(pid_str.strip())
                        pids.append(pid)
                    except ValueError:
                        continue
        
        if not pids:
            typer.echo(f"ℹ️  No processes found using port {port}")
            return True
        
        typer.echo(f"🔫 Found {len(pids)} process(es) using port {port}")
        
        # Kill each process
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
                typer.echo(f"✅ Killed process {pid}")
            except (ProcessLookupError, PermissionError) as e:
                typer.echo(f"⚠️  Failed to kill process {pid}: {e}")
                return False
        
        typer.echo(f"✅ Successfully killed all processes on port {port}")
        return True
        
    except Exception as e:
        typer.echo(f"❌ Error killing processes on port {port}: {e}")
        return False


def start_uvicorn_server(app_path: str, port: int) -> bool:
    """Start uvicorn server with live reload"""
    try:
        cmd = ["uvicorn", app_path, "--port", str(port), "--reload"]
        typer.echo(f"🚀 Starting uvicorn server: {' '.join(cmd)}")
        
        # Start the process in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        import time
        time.sleep(1)
        
        # Check if process is still running
        if process.poll() is None:
            typer.echo(f"✅ Server started successfully on port {port}")
            typer.echo(f"📊 Process ID: {process.pid}")
            typer.echo(f"🌐 Access your app at: http://localhost:{port}")
            return True
        else:
            # Process exited, get error output
            stdout, stderr = process.communicate()
            typer.echo(f"❌ Server failed to start")
            if stderr:
                typer.echo(f"Error: {stderr}")
            return False
            
    except Exception as e:
        typer.echo(f"❌ Error starting uvicorn server: {e}")
        return False


@app.command()
def fix(
    tag: str = Argument(..., help="Issue tag (e.g., bug, feature, hotfix)"),
    description: str = Argument(..., help="Brief description of the fix"),
    notes: Optional[str] = Option(
        None, "--notes", "-n", help="Optional notes about the fix"
    ),
):
    """
    Fix a single issue based on diagnostics.

    This command will:
    1. Create a new git branch (format: fix/{tag}-{description})
    2. Wait for you to apply and stage the fix manually
    3. Ask for test results
    4. Commit and push the fix
    5. Log the result in FIX_LOG.md
    """
    typer.echo("🔧 Starting fix process...")

    # Check if we're in a git repository
    repo = get_git_repo()
    if not repo:
        typer.echo("❌ Not in a git repository. Please run this from a git repository.")
        raise typer.Exit(1)

    # Create branch name
    branch_name = f"fix/{tag}-{description.replace(' ', '-').lower()}"
    typer.echo(f"🌿 Creating branch: {branch_name}")

    # Create and checkout new branch
    try:
        current_branch = repo.active_branch.name
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()
        typer.echo(f"✅ Switched to branch: {branch_name}")
    except Exception as e:
        typer.echo(f"❌ Error creating branch: {e}")
        raise typer.Exit(1)

    # Prompt user to apply fix
    typer.echo("\n📝 Please apply your fix and stage the changes.")
    typer.echo("💡 Use 'git add <files>' to stage your changes.")
    typer.echo("💡 Use 'git status' to check staged files.")

    input("\n⏳ Press Enter when you've staged your changes...")

    # Get staged files
    staged_files = get_staged_files()
    if not staged_files:
        typer.echo(
            "⚠️  No staged files detected. Are you sure you've staged your changes?"
        )
        if not typer.confirm("Continue anyway?"):
            raise typer.Exit(1)

    # Ask for test result
    typer.echo("\n🧪 Did the tests pass?")
    test_result = typer.prompt("Enter test result (PASS/FAIL)", default="PASS").upper()

    if test_result not in ["PASS", "FAIL"]:
        typer.echo("❌ Invalid test result. Please enter PASS or FAIL.")
        raise typer.Exit(1)

    # Commit the changes
    try:
        commit_message = f"fix({tag}): {description}"
        repo.index.commit(commit_message)
        typer.echo(f"✅ Committed changes: {commit_message}")
    except Exception as e:
        typer.echo(f"❌ Error committing changes: {e}")
        raise typer.Exit(1)

    # Push the branch
    try:
        origin = repo.remote("origin")
        origin.push(branch_name)
        typer.echo(f"✅ Pushed branch to remote: {branch_name}")
    except Exception as e:
        typer.echo(f"❌ Error pushing branch: {e}")
        typer.echo("💡 You may need to set up the remote or push manually.")

    # Determine status based on test result
    status = "FIXED" if test_result.upper() == "PASS" else "FAILED"

    # Log the result
    log_fix_result(
        status=status,
        tag=tag,
        files_modified=staged_files,
        summary=description,
        test_result=test_result,
        notes=notes,
    )

    typer.echo(f"\n🎉 Fix process completed! Status: {status}")
    typer.echo(f"📋 Results logged to: {FIX_LOG_FILE}")


@app.command()
def diagnose():
    """
    Run the diagnostics script to identify issues.

    This command executes the diagnostic_script.py file and outputs
    the results to the terminal.
    """
    typer.echo("🔍 Running diagnostics...")

    if not os.path.exists(DIAGNOSTIC_SCRIPT):
        typer.echo(f"❌ Diagnostic script not found: {DIAGNOSTIC_SCRIPT}")
        raise typer.Exit(1)

    # Run the diagnostic script
    result = run_command([sys.executable, DIAGNOSTIC_SCRIPT])

    if result.returncode == 0:
        typer.echo("✅ Diagnostics completed successfully")
        if result.stdout:
            typer.echo("\n📊 Diagnostic Results:")
            typer.echo(result.stdout)
    else:
        typer.echo("❌ Diagnostics failed")
        if result.stderr:
            typer.echo(f"Error: {result.stderr}")
        raise typer.Exit(1)


@app.command()
def atest():
    """
    Alias for diagnose command.

    Runs the same diagnostics as the diagnose command.
    """
    diagnose()


@app.command()
def refa():
    """
    Fully refactor and clean up the project codebase.

    This command runs:
    - black . (auto-format code)
    - isort . (organize imports)
    - flake8 (lint code)

    Changes are NOT auto-committed (safe for preview).
    """
    typer.echo("🧹 Starting code refactoring and cleanup...")

    # Check if required tools are installed
    tools = ["black", "isort", "flake8"]
    missing_tools = []

    for tool in tools:
        result = run_command([tool, "--version"], capture_output=True)
        if result.returncode != 0:
            missing_tools.append(tool)

    if missing_tools:
        typer.echo(f"❌ Missing required tools: {', '.join(missing_tools)}")
        typer.echo("💡 Install them with: pip install black isort flake8")
        raise typer.Exit(1)

    # Run black (code formatting)
    typer.echo("\n🎨 Running black (code formatting)...")
    black_result = run_command(["black", "."])
    if black_result.returncode == 0:
        typer.echo("✅ Black formatting completed")
    else:
        typer.echo("⚠️  Black formatting had issues")
        if black_result.stderr:
            typer.echo(f"Black stderr: {black_result.stderr}")

    # Run isort (import organization)
    typer.echo("\n📦 Running isort (import organization)...")
    isort_result = run_command(["isort", "."])
    if isort_result.returncode == 0:
        typer.echo("✅ isort import organization completed")
    else:
        typer.echo("⚠️  isort had issues")
        if isort_result.stderr:
            typer.echo(f"isort stderr: {isort_result.stderr}")

    # Run flake8 (linting)
    typer.echo("\n🔍 Running flake8 (code linting)...")
    flake8_result = run_command(["flake8", "."])
    if flake8_result.returncode == 0:
        typer.echo("✅ flake8 linting passed - no issues found")
    else:
        typer.echo("⚠️  flake8 found linting issues:")
        if flake8_result.stdout:
            typer.echo(flake8_result.stdout)

    typer.echo("\n🎉 Code refactoring completed!")
    typer.echo("💡 Review the changes and commit them manually if satisfied.")
    typer.echo("💡 Use 'git diff' to see what changed.")


@app.command()
def kr(
    port: int = Option(8000, "--port", "-p", help="Port to kill processes on and start server"),
    app_path: str = Option("main:app", "--app-path", "-a", help="FastAPI app path (e.g., main:app)"),
):
    """
    Kill processes on a port and restart FastAPI app with uvicorn.
    
    This command will:
    1. Kill any processes currently using the specified port
    2. Start a new uvicorn server with live reload enabled
    
    Examples:
        fixer kr                    # Use defaults (port 8000, app main:app)
        fixer kr --port 3000       # Use port 3000
        fixer kr --app-path "app:api"  # Use custom app path
    """
    typer.echo("🔄 Starting Kill & Restart process...")
    
    # Step 1: Kill processes on the port
    typer.echo(f"\n🔫 Step 1: Killing processes on port {port}")
    if not kill_processes_on_port(port):
        typer.echo("❌ Failed to kill processes. Aborting.")
        raise typer.Exit(1)
    
    # Step 2: Start uvicorn server
    typer.echo(f"\n🚀 Step 2: Starting uvicorn server")
    if not start_uvicorn_server(app_path, port):
        typer.echo("❌ Failed to start server. Aborting.")
        raise typer.Exit(1)
    
    typer.echo(f"\n🎉 Kill & Restart completed successfully!")
    typer.echo(f"💡 Server is running in background with live reload enabled")
    typer.echo(f"💡 Use Ctrl+C in the server terminal to stop the server")


if __name__ == "__main__":
    app()
