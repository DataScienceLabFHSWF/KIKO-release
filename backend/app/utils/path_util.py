import hashlib, os, re, logging

logger = logging.getLogger(__name__)

# Regular expression to match hashed filenames
HASHED_NAME_RE = re.compile(r"_[0-9a-fA-F]{32,64}\.pdf$")

def compute_sha256(data: bytes) -> str:
    """Compute SHA256 hash of the given data.
    This function takes a byte string as input and returns its SHA256 hash as a hexadecimal string.
    It is used to generate a unique identifier for the document content, ensuring that the same content always produces the same hash.
    This is useful for deduplication and content-based storage."""
    
    print("ℹ️ Computing SHA256 hash for the data.")
    if not data:
        print("❌ No data provided for hashing.")
        raise ValueError("No data provided for hashing")
    if not isinstance(data, bytes):
        print("❌ Data must be in bytes format for hashing.")
        raise ValueError("Data must be bytes for hashing")
    print("ℹ️ Data is valid for hashing.")
    # Compute SHA256 hash
    sha256_hash = hashlib.sha256(data).hexdigest()
    print(f"✅ Computed SHA256 hash: {sha256_hash}")
    return sha256_hash

def canonical_storage_path(content_hash: str) -> str:
    """Generate a canonical storage path for the document based on its content hash.
    This function creates a path in the format:
    /backend/data/uploaded_docs/<hash>.pdf
    where <hash> is the SHA256 hash of the document content.
    This ensures that the document is stored in a consistent location,
    regardless of the original file name or location."""
    
    print(f"ℹ️ Generating canonical storage path for content hash: {content_hash}")
    if not content_hash:
        print("❌ No content hash provided for generating storage path.")
        raise ValueError("No content hash provided")
    if not isinstance(content_hash, str):
        print("❌ Content hash must be a string.")
        raise ValueError("Content hash must be a string")
    print("ℹ️ Content hash is valid for generating storage path.")
    
    can_stg_path = os.path.join(os.getcwd(), "data", "uploaded_docs", f"{content_hash}.pdf")
    print(f"✅ Generated canonical storage path: {can_stg_path}")    
    return can_stg_path 

def canonical_storage_path_for_ext(
    content_hash: str, 
    ext: str
) -> str:
    """Generate a canonical storage path for arbitrary file extensions.
    Returns /data/uploaded_docs/<hash>.<ext>.
    """

    print(f"ℹ️ Generating canonical storage path for content hash: {content_hash} and ext: {ext}")
    if not content_hash or not isinstance(content_hash, str):
        print("❌ Invalid content hash provided for generating storage path.")
        raise ValueError("Invalid content hash for storage path")
    clean_ext = (ext or "").lower().lstrip('.') or "bin"
    can_stg_path = os.path.join(os.getcwd(), "data", "uploaded_docs", f"{content_hash}.{clean_ext}")
    print(f"✅ Generated canonical storage path (ext): {can_stg_path}")
    return can_stg_path

def is_probably_hashed_filename(name: str) -> bool:
    """Check if the given filename is likely a hashed filename.
    This function uses a regular expression to determine if the filename
    ends with an underscore followed by a hexadecimal string of 32 to 64 characters,
    which is typical for hashed filenames."""

    print(f"ℹ️ Checking if the filename '{name}' is probably hashed.")
    if not name or not isinstance(name, str):
        print("❌ Invalid filename provided for checking.")
        return False
    print("ℹ️ Filename is valid for checking.")
    
    # Check if the filename matches the hashed pattern
    is_hashed = bool(HASHED_NAME_RE.search(name))
    if is_hashed:
        print(f"✅ The filename '{name}' is probably hashed.")
    else:
        print(f"ℹ️ The filename '{name}' is not hashed.")
    return is_hashed    

# Helper functions used across backend API and services for path operations.

def get_folder_signature(folder_path: str) -> str:
    """Generate folder signature based on files and modification times."""
    
    print(f"ℹ️ Generating folder signature for folder path: {folder_path} and current working directory: {os.getcwd()}.")
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder does not exist: {folder_path}")
        return ""
    
    if not os.path.isdir(folder_path):
        print(f"❌ Path is not a directory: {folder_path}")
        return ""
    
    print(f"ℹ️ Folder exists and is a directory: {folder_path}")
    
    # Create a signature based on file names, modification times, and sizes
    print(f"ℹ️ Creating signature for files in the folder: {folder_path}")
    signature = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            print(f"ℹ️ Processing file PATH: {file_path}")
            mod_time = os.path.getmtime(file_path)
            print(f"ℹ️ File modification time: {mod_time}")
            file_size = os.path.getsize(file_path)
            print(f"ℹ️ File size: {file_size}")
            signature.append(f"{filename}:{mod_time}:{file_size}")
    
    print(f"ℹ️ Generated signature: {signature}")
    if not signature:
        print(f"❌ No valid files found in the folder: {folder_path}")
        return ""
    
    # Join the signature parts with a separator
    print(f"ℹ️ Joining signature parts with '|' separator.")
    # Use a pipe '|' as the separator
    result = "|".join(signature)
    print(f"ℹ️ Resulting signature: {result}")
    return result
