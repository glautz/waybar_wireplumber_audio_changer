#!/usr/bin/env python
import subprocess

# Choose menu program: "fuzzel" or "wofi"
MENU = "fuzzel"

def parse_wpctl_status():
    output = str(subprocess.check_output("wpctl status", shell=True, encoding='utf-8'))
    lines = output.replace("├", "").replace("─", "").replace("│", "").replace("└", "").splitlines()

    # --- Sinks ---
    sinks_index = next((i for i, line in enumerate(lines) if "Sinks:" in line), None)
    sinks = []
    for line in lines[sinks_index + 1:]:
        if not line.strip():
            break
        sinks.append(line.strip())
    sinks = [s.split("[vol:")[0].strip() for s in sinks]
    sinks = [s.replace("*", "").strip() + " - Default" if s.startswith("*") else s for s in sinks]
    sinks_dict = [{"id": int(s.split(".")[0]), "name": s.split(".")[1].strip(), "type": "sink"} for s in sinks]

    # --- Sources ---
    sources_index = next((i for i, line in enumerate(lines) if "Sources:" in line), None)
    sources = []
    for line in lines[sources_index + 1:]:
        if not line.strip():
            break
        sources.append(line.strip())
    sources = [s.split("[vol:")[0].strip() for s in sources]
    sources = [s.replace("*", "").strip() + " - Default" if s.startswith("*") else s for s in sources]
    sources_dict = [{"id": int(s.split(".")[0]), "name": s.split(".")[1].strip(), "type": "source"} for s in sources]

    return sinks_dict, sources_dict

# Build menu output
sinks, sources = parse_wpctl_status()
output = ''
output += "─── Sinks: ───\n"
for item in sinks:
    if item['name'].endswith(" - Default"):
        output += f" {item['name']}\n"
    else:
        output += f"{item['name']}\n"

output += "─────────────────────────────────────────\n"
output += "─── Sources: ───\n"
for item in sources:
    if item['name'].endswith(" - Default"):
        output += f" {item['name']}\n"
    else:
        output += f"{item['name']}\n"

# Build the menu command depending on MENU choice
if MENU == "fuzzel":
    menu_command = f"echo '{output}' | fuzzel --dmenu --anchor top-right --x-margin=10 --y-margin=10 --width=40 --lines=10 --hide-prompt"
elif MENU == "wofi":
    # wofi uses slightly different flags, but --dmenu works the same
    menu_command = f"echo '{output}' | wofi --show=dmenu --no-sort --hide-scroll --allow-markup --define=hide_search=true --location=top_right --width=600 --height=400 --xoffset=-40 --yoffset=10"

# Run menu
menu_process = subprocess.run(menu_command, shell=True, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if menu_process.returncode != 0:
    print("User cancelled the operation.")
    exit(0)

selected_name = menu_process.stdout.strip().replace("-> ", "").strip()

# Find selected item in sinks or sources
all_items = sinks + sources
selected_item = next(item for item in all_items if item['name'] == selected_name)

# Set default depending on type
subprocess.run(f"wpctl set-default {selected_item['id']}", shell=True)