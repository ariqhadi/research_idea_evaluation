import json
import os

NOTEBOOK_PATH = '/Users/ariq/Public/Data/Thesis/Program/Evaluation_agents/evaluation_program.ipynb'
DRAFT_CODE_PATH = '/Users/ariq/Public/Data/Thesis/Program/Evaluation_agents/gan_agents_draft.py'

def create_code_cell(source_code):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source_code.splitlines(keepends=True)
    }

def create_markdown_cell(source_text):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source_text.splitlines(keepends=True)
    }

def main():
    # Read the notebook
    with open(NOTEBOOK_PATH, 'r') as f:
        notebook = json.load(f)

    # Read the draft code
    with open(DRAFT_CODE_PATH, 'r') as f:
        draft_code = f.read()

    # Split the code into chunks (simple splitting by comments for now, or just manual indices based on my knowledge of the file)
    # Since I wrote the file, I know the structure.
    
    lines = draft_code.splitlines(keepends=True)
    
    # Chunk 1: Imports and State (Lines 0-16 approx)
    chunk1 = "".join(lines[0:16])
    
    # Chunk 2: Prompts (Lines 20-82 approx)
    chunk2 = "".join(lines[20:83])
    
    # Chunk 3: Node Functions (Lines 84-156 approx)
    chunk3 = "".join(lines[84:157])
    
    # Chunk 4: Graph Construction (Lines 157-187 approx)
    chunk4 = "".join(lines[157:187])
    
    # Chunk 5: Execution Helper (Lines 188-end)
    chunk5 = "".join(lines[188:])

    # Create new cells
    new_cells = []
    
    new_cells.append(create_markdown_cell("## GAN-like Agentic Architecture\n\nThe following cells implement an Advocate-Skeptic-Moderator flow to evaluate the research idea."))
    new_cells.append(create_code_cell(chunk1))
    new_cells.append(create_code_cell(chunk2))
    new_cells.append(create_code_cell(chunk3))
    new_cells.append(create_code_cell(chunk4))
    new_cells.append(create_code_cell(chunk5))
    
    # Example usage cell
    example_usage = """# Example Usage
# Assuming 'initial_user_input' and 'list_of_papers' (string) are available from previous cells.
# You might need to extract them from the state of the previous graph or define them manually for testing.

# Example:
# research_idea_text = initial_user_input.content 
# retrieved_papers_text = list_of_papers # Ensure this is the string representation

# result = run_gan_debate(research_idea_text, retrieved_papers_text)
# for m in result['messages']:
#     print(m.content)
"""
    new_cells.append(create_code_cell(example_usage))

    # Append to notebook
    notebook['cells'].extend(new_cells)

    # Save notebook
    with open(NOTEBOOK_PATH, 'w') as f:
        json.dump(notebook, f, indent=1)
    
    print(f"Successfully appended {len(new_cells)} cells to {NOTEBOOK_PATH}")

if __name__ == "__main__":
    main()
