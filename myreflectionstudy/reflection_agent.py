import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class QuizAgent:
    def __init__(self, model="openai/gpt-oss-120b"): #self=specific instance of QuizAgent class
        """
        Initializes the agent with an LLM client/sets up agent with a specific model and prepares it to interact with the Groq API
        """
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY")) #creates an instance of the Groq client and assigns it to the instance variable self.client
        #this client will be used to send requests to the Groq API for generating quiz content
        self.model = model #assigns the model parameter to the instance variable self.model
        #allows the agent to use the specified model when making API calls, making the model configurable
    
    def generate_quiz(self, notes:str)->str:
        """
        Generates a quiz based on the provided lecture notes.
        This is the "generation" step of the pattern.
        """

        system_prompt = """
        You are a helpful Study Assistant.  
        Your task is to generate a concise multiple-choice quiz based on the lecture notes provided by the user.  

        Requirements for quiz generation:  
        - **Length**: Create exactly 3 questions.  
        - **Answer Options**: Each question must have exactly 4 answer choices (A–D).  
        - **Correct Answer Placement**: Randomize the position of the correct answer across questions so it is not predictable.  
        - **Answer Key**: Do NOT show the correct answer immediately after each question. Instead, list all correct answers together at the very end under an "Answer Key" section.  
        - **Clarity & Accuracy**: Questions must be unambiguous, grammatically correct, factually accurate, and directly based on the lecture notes.  
        - **Plausibility**: All distractors (incorrect options) must be realistic and relevant, not obviously wrong.  
        - **Coverage**: Questions should test key points from the notes, avoiding trivial or obscure details.  
        - **Difficulty Balance**: Include a mix of straightforward and moderately challenging questions, appropriate for study review.  
        - **Question Variety**: Ensure different types of cognitive checks are used:  
        - At least one **definition/recall** question.  
        - At least one **conceptual understanding** question.  
        - At least one **application/analysis** question.  

        Formatting rules:  
        - Present questions in a numbered list.  
        - Label answer options with A, B, C, D.  
        - At the end of the quiz, include an "Answer Key" section with the correct option for each question.  

        Example structure:  
        1. [Question text]  
        A) …  
        B) …  
        C) …  
        D) …  

        2. [Question text]  
        A) …  
        B) …  
        C) …  
        D) …  

        3. [Question text]  
        A) …  
        B) …  
        C) …  
        D) …  

        **Answer Key**  
        1. B  
        2. D  
        3. A  
        """

        generation_history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here are the lecture notes:\n\n{notes}"}
        ]

        response = self.client.chat.completions.create(
            messages = generation_history,
            model = self.model,
        )

        return response.choices[0].message.content
    
    def reflect_on_quiz(self, quiz:str)->str: # decomposition of a complex task into simpler, specialized sub-tasks improves performance and reliability. A single, complex prompt asking a single model to do both can lead to what's called prompt-following breakdown, where the model gets confused or ignores parts of the instructions. By having separate prompts and potentially separate models, we give each component a single, clear objective.
        
        """
        Reflects on the generated quiz to identify areas for improvement. This is the "reflection" step of the pattern
        """
        system_prompt = """
       You are a Quality Assurance assistant for a multiple-choice quiz generation tool.  
        Your role is to rigorously evaluate each quiz with no leniency, ensuring it meets the highest quality standards.  

        You must check for ALL of the following:  
        - **Clarity & Precision**: Questions and options must be unambiguous, grammatically correct, and free from vague wording.  
        - **Integrity**: No hints, clues, patterns, or wording that reveal or bias the correct answer.  
        - **Accuracy**: Each designated correct answer must be factually and contextually correct.  
        - **Option Quality**: All distractors (incorrect options) must be plausible, relevant, and clearly incorrect without being misleading.  
        - **Consistency**: Formatting, style, and terminology must be uniform across the quiz.  
        - **Fairness**: No cultural, linguistic, or knowledge biases unless explicitly intended.  
        - **Difficulty Appropriateness**: Each question must match the intended difficulty level and the set should have a balanced difficulty range.  
        - **Completeness**: No missing answer keys, incomplete questions, or duplicated items.  

        Response rules:  
        - If the quiz fully satisfies ALL criteria, respond with exactly `<OK>`.  
        - If **any** issue is found, reject the quiz and provide a structured, specific, and actionable list of problems (e.g., “Q3: Distractor ‘C’ is too obviously incorrect compared to others”).  
        - Do not provide vague feedback; always cite the exact question and describe how to fix it.  
        - Never approve a quiz with even minor issues.
        """

        reflection_history = [
            {"role": "system", "content":system_prompt},
            {"role": "user", "content": f"Here is the quiz to review:\n\n{quiz}"}
        ]

        response = self.client.chat.completions.create(
            messages=reflection_history,
            model=self.model,
        )

        return response.choices[0].message.content
    
    def run_study_session(self, notes: str, max_iterations=3) -> str:
        """
        Orchestrates the iterative generation and reflection process.
        This is the full reflection loop.
        """
        quiz = self.generate_quiz(notes)
        print("--- Initial Quiz Generated ---")
        print(quiz)
        print("\n" + "="*50 + "\n")

        for i in range(max_iterations):
            print(f"--- Reflection Iteration {i+1}/{max_iterations} ---")
            reflection = self.reflect_on_quiz(quiz)

            if "<OK>" in reflection:
                print("Reflection successful. The quiz is good to go!")
            else:
                print("Reflection identified issues. Here's the feedback:")
                print(reflection)
                print("\nAttempting to regenerate the quiz...\n")

                # Use critique as an additional instruction for next generation
                #throwing in all the three
                regeneration_prompt = f"""
                Here are my original lecture notes:
                ---
                {notes}
                ---

                Here is the previous version of the quiz:
                ---
                {quiz}
                ---

                The following feedback was provided for the previous quiz. Please use this to generate the improved version:
                ---
                {reflection}
                ---
                """

                # The LLM's new task is to incorporate the feedback to produce a better quiz
                generation_history = [
                    {"role": "system", "content": self.generate_quiz.__doc__}, # use the original docstring as a simple system prompt
                    {"role": "user", "content": regeneration_prompt}
                ]

                new_response = self.client.chat.completions.create(
                    messages=generation_history,
                    model=self.model
                )

                quiz = new_response.choices[0].message.content
                print("\n" + "="*50 + "\n")
                print("--- Regenerated Quiz ---")
                print(quiz)
        
        print("\nMax iterations reached. Final quiz:")
        return quiz
        

agent = QuizAgent()
text = """
# Comprehensive RDBMS Study Notes



## 1. Components of RDBMS



### Core Components

**Hardware**

- Physical devices and infrastructure on which the database system runs

- Includes servers, storage devices, and networking equipment



**Software** 

- Database management software that handles data storage, retrieval, and manipulation

- Provides the interface between users and the physical data storage



**Users**

- End users who interact with the database system

- Include database administrators, application developers, and business users



**Database Access Language**

- Primary communication interface between users and the DBMS

- SQL (Structured Query Language) is the most common example

- Enables users to query, insert, update, and delete data



**Data**

- The actual information stored and managed within the system

- Organized in structured formats within tables and relationships



**Procedures**

- Instructions, rules, and protocols that govern database operations

- Include backup procedures, security protocols, and maintenance routines



### System Flow and Interaction

The interaction flow follows this pattern:

1. Users interact with the Database Access Language, Data, and Procedures

2. These interactions are processed through the Software layer

3. The Software ultimately executes operations on the Hardware infrastructure



## 2. RDBMS Characteristics



### Key Design Principles



**Easy Maintenance**

- System architecture designed for straightforward maintenance and updates

- Modular design allows for component-level maintenance without system-wide disruption



**Data Correlation Capability**

- Ability to establish relationships between different data sets

- Supports evolving business requirements through flexible data connections



**Minimum Redundancy**

- Eliminates unnecessary data duplication across the system

- Implements normalization principles to reduce storage waste and inconsistencies



**Independent Central Repository**

- All data managed from a single, centralized location

- Provides unified data governance and control



**Integrated Database Structure**

- Data components work together seamlessly

- Ensures consistency and coherence across all database operations



**Automatic Recovery**

- Built-in mechanisms for system recovery from failures

- Includes backup systems, transaction logs, and rollback capabilities



## 3. Database Management Systems Overview



### RDBMS vs Traditional DBMS



**Relational Database Management Systems (RDBMS)**

- Store data in interconnected tables with clearly defined relationships

- Use unique identifiers (like roll numbers) to link related information across multiple tables

- Example: Student data linked across marks, attendance, and payment records through roll number

- Require tabular data structure with well-defined storage formats

- Support referential integrity and complex queries



**Traditional DBMS**

- Store data without required relationships between tables

- Similar to a library system where various unrelated documents coexist

- Accept any file structure including documents, images, and videos

- Lack structured connections between data elements

- Provide flexibility but limit structured data management capabilities



### Modern Hybrid Systems

- Utilize ETL (Extraction, Transformation, and Loading) processes

- Convert unstructured data from traditional systems into structured RDBMS format

- Bridge the gap between flexible storage and structured analysis

- Enable better data analysis and reporting capabilities



### Architecture Support

- RDBMS supports client-server architecture for online transactions

- Enables distributed services with data replication across multiple servers

- Provides enhanced safety, availability, and performance through distributed architecture



## 4. Data Structure Types and Analysis



### Data Classification



**Structured Data**

- Exists in tabular format with clearly defined columns

- Examples: Name, age, course information in database tables

- Easily queryable and analyzable using SQL

- Fits well into traditional relational database models



**Unstructured Data**

- Includes documents, images, PDFs, and multimedia files

- Lacks predefined data models or organization

- Requires specialized tools for analysis and processing

- Common in content management and document storage systems



**Semi-Structured Data**

- Uses formats like JSON and XML

- Provides more structure than unstructured data but less than fully structured data

- Common in web and mobile applications for data transport

- Offers descriptive markup superior to traditional flat file formats



### Data Transport Protocols

- JSON and XML serve as primary data exchange formats between clients and servers

- Essential for web and mobile application development

- Provide standardized methods for data communication across different platforms



## 5. Database Architecture Tiers



### Single-Tier Architecture

**One-Tier DBMS**

- Involves direct local database access

- No network services required

- Simple but limited scalability

- Suitable for standalone applications



### Multi-Tier Architecture

**Enhanced Security and Accessibility**

- Demonstrates improved database security through layered approach

- Example: E-commerce payment systems using intermediary services like Pesapal

- Applications connect through intermediary database services rather than direct cloud connections

- Provides better security, scalability, and maintainability



**Benefits of Multi-Tier Systems**

- Separation of concerns between presentation, business logic, and data layers

- Enhanced security through controlled access points

- Improved scalability and performance optimization

- Better maintenance and update capabilities



## 6. Database Modeling Approaches



### Fundamental Modeling Principles

**Importance of Planning**

- Database modeling requires creating logical templates before physical construction

- Similar to architectural design where blueprints precede building construction

- Essential for ensuring efficient and effective database structures



**Logical vs Physical Design**

- Logical design focuses on data relationships and business rules

- Physical design addresses storage, indexing, and performance optimization

- Both phases critical for successful database implementation



### Practical Modeling Example: Student Tracking System



**Central Facts Table (Biodata)**

- Contains core student personal information

- Serves as the primary reference point for all related data

- Uses unique identifiers (roll numbers) for relationship establishment



**Subsidiary Tables**

- **Attendance Table**: Tracks attendance across six course units

- **Performance Table**: Records assignments, exams, and grades

- **Subjects Table**: Maintains course and subject information

- **Semesters Table**: Organizes academic term data



**Relationship Maintenance**

- All tables connected through roll number relationships

- Ensures data integrity and consistency across the system

- Enables comprehensive student information retrieval



## 7. Database Model Types



### Hierarchical Model

**Structure and Organization**

- Organizes data in tree-like structures with root and terminal nodes

- Follows priority-based relationships similar to family hierarchies

- Examples include organizational charts and file system structures



**Characteristics**

- Clear parent-child relationships

- Efficient for representing naturally hierarchical data

- Limited flexibility for complex relationships



### Network Model

**Enhanced Flexibility**

- Provides multiple relationship paths between data entities

- Allows complex data retrieval from various database connection points

- Supports many-to-many relationships more effectively than hierarchical models



**Advantages**

- More flexible than hierarchical models

- Better representation of complex business relationships

- Improved data access patterns



### Relational Model

**Relationship Through Attributes**

- Establishes relationships through shared table columns

- Enables intuitive data retrieval by querying specific attributes

- Example: Query student name to find corresponding contact information



**Key Strengths**

- Excellent data retrieval capabilities through attribute-based queries

- Supports complex queries using SQL

- Provides strong theoretical foundation through relational algebra



## 8. Entity-Relationship Modeling



### Visual Representation Standards

**Entities (Objects)**

- Represented in solid rectangles

- Represent real-world objects or concepts in the database



**Relationships (Actions)**

- Depicted in rhombus (diamond) shapes

- Show how entities interact with each other



**Relationship Strength Indicators**

- **Solid Rhombus**: Indicates strong, mandatory relationships

- **Double-Walled Rhombus**: Shows weak or optional relationships



### Attribute Classifications



**Key Attributes**

- Uniquely identify individual entity instances

- Essential for maintaining entity integrity and relationships

- Cannot be null and must be unique across all instances



**Composite Attributes**

- Combine multiple key attributes into a single logical unit

- Can be broken down into constituent parts

- Example: Full address composed of street, city, state, zip code



**Derived Attributes**

- Calculate values based on other stored attributes

- Not physically stored but computed when needed

- Example: Age calculated from birth date and current date



**Multi-Valued Attributes**

- Accept multiple values for a single entity instance

- Example: A person having multiple phone numbers or email addresses

- Often implemented through separate related tables in physical design
"""
#quiz = agent.generate_quiz(text)
#print(quiz)
#reflection = agent.reflect_on_quiz(quiz)
#print(reflection)
final_combined = agent.run_study_session(text, 3)
print(final_combined)