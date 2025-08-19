# Reflection-Study

A Python-based study assistant that generates and iteratively improves multiple-choice quizzes from lecture notes using the Groq API and a reflection loop.

## Features

- **Quiz Generation:** Automatically creates concise, high-quality multiple-choice quizzes from your study notes.
- **Reflection Loop:** Evaluates quizzes for clarity, accuracy, and quality, then regenerates improved versions based on feedback.
- **Configurable Model:** Uses Groq's LLM (default: `openai/gpt-oss-120b`).
- **Environment Variable Support:** API keys and secrets managed via `.env` file.

## Project Structure

```
Reflection-Study/
│
├── reflection_agent.py      # Main agent code
├── README.md                # Project documentation
├── myreflectionstudy/
│   ├── .env                 # API keys (ignored by git)
│   ├── .gitignore           # Ignore venv and sensitive files
│   ├── pyvenv.cfg           # Virtual environment config
│   ├── Include/             # venv include files
│   ├── Lib/                 # venv libraries
│   └── Scripts/             # venv scripts
```

## Setup

1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd Reflection-Study
   ```

2. **Create a virtual environment (if not already present):**
   ```sh
   python -m venv myreflectionstudy
   ```

3. **Activate the virtual environment:**
   - **Windows:**
     ```sh
     myreflectionstudy\Scripts\activate
     ```
   - **macOS/Linux:**
     ```sh
     source myreflectionstudy/bin/activate
     ```

4. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
   *(Create `requirements.txt` with needed packages: `groq`, `python-dotenv`)*

5. **Set up your `.env` file:**
   ```
   GROQ_API_KEY="your_groq_api_key_here"
   ```

## Usage

Edit `reflection_agent.py` to provide your lecture notes.  
Run the script:

```sh
python reflection_agent.py
```

The agent will generate a quiz, reflect on its quality, and iteratively improve it.