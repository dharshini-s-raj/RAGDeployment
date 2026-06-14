import os
import time
import mimetypes
from pathlib import Path

from dotenv import load_dotenv
from google import genai
import os
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY, vertexai=False)
def guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"
 
 
def wait_operation(op, poll_s: float = 2.0):
    while not getattr(op, "done", False):
        time.sleep(poll_s)
        op = client.operations.get(op)
    err = getattr(op, "error", None)
    if err:
        raise RuntimeError(f"Operation failed: {err}")
    return op
 
 
def get_or_create_store(display_name: str):
    for s in client.file_search_stores.list():
        if getattr(s, "display_name", None) == display_name:
            return s
    return client.file_search_stores.create(config={"display_name": display_name})
 
DATA_DIR = Path("data")
if not DATA_DIR.exists():
    raise FileNotFoundError(f"Folder not found: {DATA_DIR.resolve()}")
 
STORE_DISPLAY_NAME = "deployment-store1"  # change if you want
 
 
store = get_or_create_store(STORE_DISPLAY_NAME)
store_name = store.name  # looks like "fileSearchStores/...."
store_name
 
files = [p for p in DATA_DIR.rglob("*") if p.is_file()]
len(files), [str(p.relative_to(DATA_DIR)) for p in files[:10]]
 
uploaded_relpaths = []
 
for p in files:
    rel = p.relative_to(DATA_DIR)
    mime = guess_mime(p)
 
    print(f"Uploading: {rel}  (mime={mime})")
 
    op = client.file_search_stores.upload_to_file_search_store(
        file_search_store_name=store_name,
        file=str(p),
        config={
            "display_name": str(rel),   # shows up in citations later
            "mime_type": mime,
            "custom_metadata": [
                {"key": "rel_path", "string_value": str(rel)},
                {"key": "ext", "string_value": p.suffix.lower().lstrip(".")},
            ],
        },
    )
    wait_operation(op)
    uploaded_relpaths.append(str(rel))
 
print(f"Uploaded {len(uploaded_relpaths)} files into {store_name}")
 
def count_documents_in_store(store_name: str) -> int:
    # lists processed "documents" inside the File Search store
    return sum(1 for _ in client.file_search_stores.documents.list(parent=store_name))
 
 
target = len(uploaded_relpaths)
timeout_s = 900
poll_s = 3
 
t0 = time.time()
while True:
    doc_count = count_documents_in_store(store_name)
    print(f"Documents indexed: {doc_count}/{target}")
 
    if doc_count >= target:
        print("Store is ready for retrieval.")
        break
 
    if time.time() - t0 > timeout_s:
        raise TimeoutError(f"Timed out waiting for indexing. Indexed {doc_count}/{target}")
 
    time.sleep(poll_s)