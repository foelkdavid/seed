import os
import re
import sys
import shutil
import subprocess
from datetime import date
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# ------------------------------
# CONFIG
# ------------------------------

TEMPLATE_DIR = Path(__file__).parent / "templates"
VALID_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")

# ------------------------------
# COLORS
# ------------------------------

BLUE = "\033[1;34m"
GREEN = "\033[1;32m"
RED = "\033[1;31m"
RESET = "\033[0m"

def info(msg):
    print(f"{BLUE}[+] {msg}{RESET}")

def success(msg):
    print(f"{GREEN}[✓] {msg}{RESET}")

def error(msg):
    print(f"{RED}[!] {msg}{RESET}")
    sys.exit(1)

# ------------------------------
# TEMPLATE RENDERING
# ------------------------------

def render_template_dir(template_path, output_path, context):
    env = Environment(loader=FileSystemLoader(str(template_path)), keep_trailing_newline=True)
    for root, dirs, files in os.walk(template_path):
        rel_dir = Path(root).relative_to(template_path)
        dest_dir = output_path / rel_dir
        dest_dir.mkdir(parents=True, exist_ok=True)

        for file in files:
            src_file = Path(root) / file
            is_template = file.endswith(".j2")
            dest_file_name = file[:-3] if is_template else file

            # Arduino special case: rename project.ino.j2 → <project>.ino
            if dest_file_name == "project.ino":
                dest_file_name = f"{context['project']}.ino"

            dest_file = dest_dir / dest_file_name

            if is_template:
                template = env.get_template(str((rel_dir / file).as_posix()))
                rendered = template.render(context)
                with open(dest_file, "w") as f:
                    f.write(rendered)
            else:
                shutil.copy2(src_file, dest_file)

# ------------------------------
# VALIDATION
# ------------------------------

def validate_project_name(name):
    if not VALID_NAME_RE.fullmatch(name):
        error("Project name must contain only letters, numbers, underscores or dashes.")

# ------------------------------
# TEMPLATE LISTING
# ------------------------------

def list_templates():
    print("Available templates:")
    for tdir in TEMPLATE_DIR.iterdir():
        if tdir.is_dir():
            print(f"  - {tdir.name}")
    sys.exit(0)

# ------------------------------
# MAIN
# ------------------------------

def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        list_templates()

    if len(sys.argv) != 3:
        print("Usage: seed <type> <project-name>")
        print("       seed --list")
        sys.exit(1)

    template_type = sys.argv[1]
    project_name = sys.argv[2]
    validate_project_name(project_name)

    src_template_dir = TEMPLATE_DIR / template_type
    if not src_template_dir.exists():
        error(f"Template type '{template_type}' not found.")

    target_dir = Path(project_name)
    if target_dir.exists():
        error(f"Directory '{project_name}' already exists.")

    context = {
        "project": project_name,
        "author": os.environ.get("USER", "unknown"),
        "date": date.today().isoformat()
    }

    info(f"Creating project '{project_name}' from template '{template_type}'...")
    render_template_dir(src_template_dir, target_dir, context)

    info(f"Initializing git repository in {project_name}/")
    subprocess.run(["git", "init"], cwd=str(target_dir), check=True)

    if template_type == "python":
        info("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"], cwd=str(target_dir), check=True)
        success("Python virtual environment created in .venv/")
        print(f"{BLUE}To activate: source {project_name}/.venv/bin/activate{RESET}")

<<<<<<< HEAD
=======
    if template_type == "esp":
        ino_path = target_dir / "project.ino"
        final_ino = target_dir / f"{project_name}.ino"
        if ino_path.exists():
            ino_path.rename(final_ino)
            success(f"Renamed sketch file to {final_ino.name}")

>>>>>>> 5101665905687328493c42dfb986ca81b16f0f6b
    success("Done.")

if __name__ == "__main__":
    main()

