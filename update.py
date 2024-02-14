import os

def convert_filename(old_filename, character_name):
    parts = old_filename.split('-')
    new_filename = None
    if len(parts) == 3 and old_filename.endswith('.txt'):
        # Guild-Channel-MessageID format
        new_filename = f"{parts[0]}-{parts[1]}-{character_name}.json"
    elif len(parts) == 2 and old_filename.endswith('.txt'):
        # Author-BotName format
        new_filename = f"{parts[0]}-{character_name}.json"
    return new_filename

def update_filenames(character_name):
    for filename in os.listdir('.'):
        new_filename = convert_filename(filename, character_name)
        if new_filename:
            os.rename(filename, new_filename)
            print(f"Renamed '{filename}' to '{new_filename}'")

def update_version_in_env(current_version):
    version_updated = False
    env_lines = []
    with open('.env', 'r') as file:
        for line in file:
            if line.startswith('VERSION='):
                if line.strip() != f'VERSION={current_version}':
                    env_lines.append(f'VERSION={current_version}\n')
                    version_updated = True
                else:
                    env_lines.append(line)
            else:
                env_lines.append(line)

    if not any(line.startswith('VERSION=') for line in env_lines):
        env_lines.append(f'VERSION={current_version}\n')
        version_updated = True

    with open('.env', 'w') as file:
        file.writelines(env_lines)
    return version_updated

def check_and_run_update(character_name, current_version):
    if update_version_in_env(current_version):
        print("Updating to new version...")
        update_filenames(character_name)
        print("Update complete!")
