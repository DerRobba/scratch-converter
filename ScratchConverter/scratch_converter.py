import argparse
import os
import zipfile
import json
import sys
from openai import OpenAI
from dotenv import load_dotenv

def create_system_prompt():
    """
    Creates the system prompt for the OpenAI API to guide the conversion process.
    """
    return """
You are an expert Scratch to Python converter. Your task is to convert a Scratch project's `project.json` into a single, executable Python file using the Pygame library.

**Input:** The user will provide the JSON content of a `project.json` file.

**Output:** You must provide ONLY the raw Python code for the Pygame application. Do not include any explanations, comments, or markdown code blocks like ```python ... ```.

**Conversion Rules:**

1.  **Goal:** The Python code should be a faithful-as-possible Pygame implementation of the Scratch project.
2.  **Simplicity over Complexity:** If a Scratch feature is exceptionally complex (e.g., intricate custom blocks, pen extensions, complex cloning), you may simplify or omit it to ensure the generated code is reliable and runs without errors. The priority is a working, stable application.
3.  **Asset Handling:**
    - Assume all image and sound assets from the Scratch project are extracted into an `assets/` subdirectory.
    - The Python code must load all assets (images for sprites/costumes, sounds) from this `assets/` directory. For example: `pygame.image.load(os.path.join('assets', 'costume1.png'))`.
4.  **Mapping Scratch Concepts to Pygame:**
    - **Stage:** The main Pygame display surface.
    - **Sprites:** Python classes, preferably inheriting from `pygame.sprite.Sprite`.
    - **Costumes:** Images loaded into `pygame.Surface` objects. A sprite should manage its own costumes.
    - **Sounds:** Sounds loaded using `pygame.mixer`.
    - **Variables:** Global variables or class attributes.
    - **`when flag clicked`:** This maps to the initialization code before the main game loop and the loop itself.
    - **`forever` loop:** The main `while True:` game loop in Python.
    - **Events (`when key pressed`, `when sprite clicked`):** These should be handled in the Pygame event loop (`for event in pygame.event.get():`).
    - **Broadcasts:** Can be implemented using Pygame's custom user events (`pygame.event.Event(pygame.USEREVENT, ...)`) or simple function/method calls between sprites.
    - **Motion Blocks (`move`, `go to`):** Update the `self.rect.x` and `self.rect.y` attributes of the sprite.
    - **Looks Blocks (`show`, `hide`, `switch costume`):** Manage sprite visibility and which `self.image` surface is currently active.
    - **Sensing (`touching ...?`):** Use Pygame collision detection functions like `pygame.sprite.spritecollide()` or `self.rect.colliderect()`.
5.  **Code Structure:**
    - The generated file must be a single, self-contained Python script.
    - It should start with necessary imports (`pygame`, `os`, `sys`).
    - Initialize Pygame and the display.
    - Define sprite classes.
    - Set up the main game loop.
    - The script should handle the `QUIT` event to close properly.
"""

def convert_sb3_to_pygame(sb3_path, output_path):
    """
    Converts an .sb3 file to a Pygame project.
    """
    load_dotenv()
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("API_BASE")
    model = os.getenv("MODEL")

    if not all([api_key, base_url, model]):
        print("Error: API_KEY, API_BASE, and MODEL must be set in the .env file.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=base_url)

    # 1. Extract project.json and assets from .sb3 file
    try:
        with zipfile.ZipFile(sb3_path, 'r') as archive:
            project_json_str = archive.read('project.json').decode('utf-8')
            
            # Create output directory if it doesn't exist
            os.makedirs(output_path, exist_ok=True)
            assets_path = os.path.join(output_path, 'assets')
            os.makedirs(assets_path, exist_ok=True)

            # Extract all assets
            for file_info in archive.infolist():
                if file_info.filename != 'project.json':
                    archive.extract(file_info, assets_path)

    except (FileNotFoundError, zipfile.BadZipFile) as e:
        print(f"Error reading or processing sb3 file: {e}", file=sys.stderr)
        sys.exit(1)

    # 2. Send to OpenAI for conversion
    print("Sending project.json to AI for conversion...")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": create_system_prompt()},
                {"role": "user", "content": project_json_str}
            ]
        )
        pygame_code = response.choices[0].message.content
    except Exception as e:
        print(f"Error communicating with OpenAI API: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Save the generated Python file
    output_file_path = os.path.join(output_path, 'main.py')
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(pygame_code)

    print(f"Conversion successful! Pygame project saved in: {output_path}")
    print(f"To run, navigate to the directory and execute: python {os.path.basename(output_file_path)}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Scratch 3 (.sb3) files to Pygame projects using AI.')
    parser.add_argument('sb3_file', help='Path to the input .sb3 file.')
    parser.add_argument('-o', '--output', default='output_pygame_project', help='Path to the output directory for the generated project.')
    
    args = parser.parse_args()
    
    convert_sb3_to_pygame(args.sb3_file, args.output)