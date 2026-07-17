import torch

def lang_display(response_language: str) -> str:
    """Map codes to display strings for the prompt."""

    m = {
        "de": "Deutsch", 
        "deu": "Deutsch", 
        "ger": "Deutsch",
        "en": "English",
        "eng": "English"
    }

    return m.get(response_language.lower(), response_language)

def get_device_and_dtype():
    """Determine if CUDA is available and set device and dtype accordingly."""

    has_cuda = torch.cuda.is_available()
    device = "cuda:0" if has_cuda else "cpu"
    dtype = torch.float32 if device == "cuda:0" else torch.bfloat16
    if has_cuda:
        props = torch.cuda.get_device_properties(0)
        print(f"✅ CUDA available: {props.name} ({round(props.total_memory/1024**3)} GB), CC {props.major}.{props.minor}")
        
    else:
        print("ℹ️ CUDA NOT available — running on CPU.")
    
    print(f"ℹ️ Using device: {device}, dtype: {dtype}")
    return device, dtype

def default_avatar_for_role(
    role: str, 
    seed: str
) -> str:
    """
    Simple role-based avatar using Dicebear.
    You can swap styles per role if you like.
    """
    
    style_by_role = {
        "Learner": "thumbs",
        "Instructor": "identicon",
        "Admin": "thumbs"
    }
    style = style_by_role.get(role, "thumbs")
    # NOTE: avatar is NOT asked on FE; we generate it here:
    avatar = f"https://api.dicebear.com/7.x/{style}/svg?seed={seed}"
    return avatar
