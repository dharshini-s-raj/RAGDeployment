from huggingface_hub import login, whoami
import os
import sys
from pathlib import Path

# Load from .env if python-dotenv is available, otherwise parse .env manually
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    env_path = Path('.') / '.env'
    if env_path.exists():
        with env_path.open() as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                k, v = line.split('=', 1)
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k.strip(), v)

token = os.getenv("HF_TOKEN")
if not token:
    print("No HF_TOKEN found. Create a .env file with HF_TOKEN=your_token or set HF_TOKEN in your environment.")
    sys.exit(1)

try:
    login(token=token)
    info = whoami()
    name = info.get('name') if isinstance(info, dict) else str(info)
    print(f"✓ Successfully logged in as: {name}")
except Exception as e:
    print(f"✗ Login failed: {e}")
    sys.exit(1)
