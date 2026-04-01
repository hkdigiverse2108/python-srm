import os
import re

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
MODULES_DIR = os.path.join(BACKEND_DIR, "app", "modules")

print("Starting MongoDB Database namespace mapping...")

# 1. Update .env file
env_path = os.path.join(BACKEND_DIR, ".env")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        content = f.read()
    new_content = content.replace("cluster0.lcbyqbq.mongodb.net/aisetu_srm", "cluster0.lcbyqbq.mongodb.net/aisetu_db")
    with open(env_path, "w") as f:
        f.write(new_content)
    print("Updated .env with aisetu_db")

# 2. Update config.py defaults
config_path = os.path.join(BACKEND_DIR, "app", "core", "config.py")
if os.path.exists(config_path):
    with open(config_path, "r") as f:
        content = f.read()
    new_content = content.replace("27017/aisetu_srm", "27017/aisetu_db")
    with open(config_path, "w") as f:
        f.write(new_content)
    print("Updated backend/app/core/config.py with aisetu_db default")

# 3. Update main.py init_beanie hardcoded db_name
main_path = os.path.join(BACKEND_DIR, "app", "main.py")
if os.path.exists(main_path):
    with open(main_path, "r") as f:
        content = f.read()
    new_content = content.replace('db_name = "aisetu_srm"', 'db_name = "aisetu_db"')
    new_content = new_content.replace('DB: aisetu_srm', 'DB: aisetu_db')
    with open(main_path, "w") as f:
        f.write(new_content)
    print("Updated backend/app/main.py with aisetu_db")

# 4. Search and Replace all collection names in models.py
modified_files = 0
for root, dirs, files in os.walk(MODULES_DIR):
    for filename in files:
        if filename == "models.py":
            file_path = os.path.join(root, filename)
            with open(file_path, "r") as f:
                original = f.read()
            
            # Find all `name = "something"` under Settings
            # Make sure to not double-prefix if already prefixed
            def replacement(match):
                prefix, name = match.group(1), match.group(2)
                if not name.startswith("srm_"):
                    return f'{prefix}"srm_{name}"'
                return match.group(0) # unchanged

            modified = re.sub(r'(class\s+Settings:[\s\S]*?name\s*=\s*)"([^"]+)"', replacement, original)
            
            if modified != original:
                with open(file_path, "w") as f:
                    f.write(modified)
                modified_files += 1
                module_name = os.path.basename(os.path.dirname(file_path))
                print(f"Updated collection prefixes in {module_name}/models.py")

print(f"Update complete! {modified_files} model files altered.")
