import os

class PromptManager:
    """Manages loading of enhanced prompt templates based on language."""
    
    def __init__(self, config):
        """Initialize with config; currently only uses 'app_config' for 'prompt_templates_dir', 
        but can be extended for future options. config should contain 'app_config' with 'prompt_templates_dir' setting."""
        self.prompt_dir = config.get("app_config").prompt_templates_dir
    
    def load_prompt_template(
        self, 
        template_name: str, 
        lang: str
    ) -> str:
        """Load a prompt template by name and language. 
        Expects templates to be named like '{template_name}_{lang}.txt' in the prompt_templates_dir.
        Returns the content of the template file as a string. Raises FileNotFoundError if the template file is not found."""
        
        template_name = f"{template_name}_{lang}.txt"
        template_path = os.path.join(self.prompt_dir, template_name)

        if not os.path.isfile(template_path):
            print(f"❌ Prompt template '{template_name}' not found at: {template_path}")
            raise FileNotFoundError(f"Prompt template '{template_name}' not found at: {template_path}")
        
        print(f"✅ Successfully loaded prompt template: {template_name} from {template_path}")
        
        # Read the template file
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
