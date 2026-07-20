# Workspace-Setup-Assignment-

Task 1 - Create the Virtual Environment and Install Dependencies
Create a Python virtual environment inside your project directory using the built-in venv module:

# macOS and Linux
python3 -m venv venv
 
# Windows
python -m venv venv
Activate your environment:

# macOS and Linux
source venv/bin/activate
 
# Windows
venv\Scripts\activate
Install the following packages, which represent a standard data analytics stack:

pip install pandas numpy matplotlib seaborn jupyter scikit-learn python-dotenv openpyxl
Confirm the environment is working by running python -c "import pandas; print(pandas.__version__)" without errors. You will capture these dependencies in Task 4.

Task 2 - Create the Project Folder Structure
Inside your repository root, create the following directory structure. Each directory must exist and contain at least one file so Git tracks it - use an empty .gitkeep file or a brief markdown file explaining the directory purpose:

analytics-workspace-setup/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── scripts/
├── output/
In each directory, add a brief markdown file (for example data/raw/README.md) explaining what belongs there. One sentence per directory is sufficient. This documents the convention for future team members.

Task 3 - Create a .gitignore File
Create a .gitignore file at the root of your repository. It must exclude at minimum:

The virtual environment folder (venv/ and .venv/), the .env file that will hold secrets, Python cache files (__pycache__/ and *.pyc), Jupyter notebook checkpoint folders (.ipynb_checkpoints/), and any operating system artifacts (.DS_Store on macOS, Thumbs.db on Windows).

You may use gitignore.io at https://www.toptal.com/developers/gitignore to generate a complete Python and Jupyter gitignore as a starting point, then review and customize it for this project.

Confirm the gitignore is working by verifying that git status does not list the venv folder after you commit.

Task 4 - Capture Dependencies in requirements.txt
With your virtual environment still active, generate a requirements.txt file using pip freeze:

pip freeze > requirements.txt
Open the file and verify it lists all the packages you installed in Task 1 with their exact version numbers. Commit this file to your repository.

To confirm the requirements.txt works, test it in a clean environment: create a second virtual environment in a temporary folder outside your project, activate it, and run pip install -r requirements.txt. If it installs without errors, your requirements.txt is correct.

Task 5 - Write the README
Create a README.md at the project root. It must contain four sections:

A brief project description explaining what this workspace is for. A Setup section with numbered steps to clone the repo, create the virtual environment, activate it, and install dependencies - using exact commands that work on both macOS/Linux and Windows. A Project Structure section listing each directory and its purpose in one sentence. A Notes section that mentions what environment variables are needed and that a teammate should copy .env.example to .env and fill in their own values.

Also create a .env.example file at the project root showing the structure of required environment variables with placeholder values. This file should be committed. The actual .env file should not be.

When your README is complete, test it using this rule: give the README to someone who has not seen the project and check whether they can set up the environment without asking you a single question.

Once all five tasks are done, commit everything with a clear message and push:

git add .
git commit -m "setup: create venv, folder structure, gitignore, requirements.txt, and README"
git push origin setup/dev-environment
Open a PR from setup/dev-environment to main in your forked repository.
