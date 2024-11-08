def load_env(env_path=".env") -> None:
    """Load environment variables from a .env file."""
    import os
    
    try:
        with open(env_path, "r") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip("'").strip('"')
                    os.environ[key] = value
                    
    except FileNotFoundError:
        print(f"File {env_path} not found.")
        
    except Exception as e:
        print(f"Error loading environment variables: {e}")
        
        
    
    