
import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("Python 3.7 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    print("\n Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("Pip upgraded successfully")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f" Failed to install dependencies: {e}")
        return False

def setup_environment():
    print("\n Setting up environment...")
    env_file = Path(".env")
    env_example = Path(".env.example")
    if env_file.exists():
        print(".env file already exists")
        return True
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("Created .env file from template")
        print("Please edit .env and add your OpenAI API key")
        return True
    else:
        with open(env_file, 'w') as f:
            f.write("# OpenAI Configuration\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
            f.write("OPENAI_MODEL=gpt-3.5-turbo\n\n")
            f.write("# Vector Database Configuration\n")
            f.write("VECTOR_DB_PATH=vector_db.pkl\n")
            f.write("EMBEDDING_MODEL=all-MiniLM-L6-v2\n")
        print("Created .env file")
        print("Please edit .env and add your OpenAI API key")
        return True
def test_imports():
    print("\n Testing imports...")
    required_packages = [
        "openai",
        "numpy",
        "sklearn",
        "sentence_transformers"
    ]
    failed_imports = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"{package}")
        except ImportError:
            print(f"{package}")
            failed_imports.append(package)   
    if failed_imports:
        print(f"\n Failed to import: {', '.join(failed_imports)}")
        print("Try running: pip install -r requirements.txt")
        return False
    print("All packages imported successfully")
    return True

def create_sample_docs():
    print("\n Creating sample documents...")
    sample_docs = {
        "sample_syllabus.txt": """
Computer Science 101 - Introduction to Programming

Instructor Information:
- Name: Dr. Jane Smith
- Email: j.smith@university.edu
- Office: CS Building, Room 205
- Office Hours: Tuesdays and Thursdays, 2:00-4:00 PM

Course Description:
This course provides an introduction to computer programming using Python.
Students will learn fundamental programming concepts, data structures, and algorithms.

Grading Policy:
- Programming Assignments: 50%
- Midterm Exam: 20%
- Final Exam: 25%
- Class Participation: 5%

Late Submission Policy:
Assignments submitted after the deadline will lose 10% per day late.
No assignments will be accepted more than 5 days after the deadline.
Extensions may be granted for documented emergencies.

Academic Integrity:
All work must be completed independently unless group work is explicitly assigned.
Collaboration on concepts is encouraged, but sharing code is prohibited.
        """.strip(),
        
        "assignment_policy.txt": """
Programming Assignment Guidelines

Submission Requirements:
1. Code must be well-commented and follow PEP 8 style guidelines
2. Include a README file explaining how to run your program
3. All files must be submitted through the course management system
4. File naming: lastname_firstname_assignment#.py

Grading Criteria:
- Correctness (60%): Does the program work as specified?
- Style (20%): Is the code well-organized and readable?
- Documentation (20%): Are comments clear and helpful?

Getting Help:
- Attend office hours for individual assistance
- Post questions on the course forum
- Form study groups with classmates
- Email the instructor for urgent issues

Common Mistakes to Avoid:
- Not testing edge cases
- Poor variable naming
- Missing error handling
- Inadequate comments
        """.strip(),
        
        "faq.txt": """
Frequently Asked Questions

Q: What should I do if I'm struggling with an assignment?
A: Come to office hours, post on the discussion forum, or email the instructor.

Q: Can I work with other students on assignments?
A: You can discuss concepts, but all code must be written independently.

Q: What happens if I miss a deadline?
A: Late assignments lose 10% per day. Contact the instructor immediately if you have an emergency.

Q: How do I set up the programming environment?
A: Follow the setup guide posted on the course website. Ask for help during office hours if needed.

Q: What topics will be covered on the midterm?
A: All material covered in lectures and assignments up to week 7.

Q: Is attendance mandatory?
A: While not mandatory, attendance strongly correlates with success in the course.

Q: Can I use AI tools like ChatGPT for assignments?
A: Limited use is allowed for learning concepts, but final submissions must be your own work.
        """.strip()
    }
    
    created_count = 0
    for filename, content in sample_docs.items():
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Created {filename}")
            created_count += 1
        else:
            print(f"⚠️  {filename} already exists")
    
    if created_count > 0:
        print(f"Created {created_count} sample documents")
    return True

def run_quick_test():
    print("\n Running quick test...")
    
    try:
        from student_email_chatbot import VectorDatabase   
        db = VectorDatabase()
        test_content = "Office hours are Tuesdays and Thursdays from 2-4 PM in room 205."
        chunks = db.add_document(test_content, "test_doc.txt")
        if chunks:
            print("Vector database test passed")
            
            results = db.search_similar("when are office hours", top_k=1)
            if results:
                print("Vector search test passed")
                return True
            else:
                print("Vector search test failed")
                return False
        else:
            print("Vector database test failed")
            return False
            
    except Exception as e:
        print(f" Quick test failed: {e}")
        return False

def main():
    print("Student Email Chatbot Setup")
    print("=" * 40)
    
    if not check_python_version():
        return False
    
    if not install_dependencies():
        return False
    
    if not setup_environment():
        return False
    
    if not test_imports():
        return False
    
    create_sample_docs()
    
    if not run_quick_test():
        print("\n Quick test failed, but setup completed")
        print("Please check your configuration and try running the example manually")
    
    print("\n Setup completed successfully!")
    print("\Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: python example_usage.py")
    print("3. Or run: python student_email_chatbot.py for a demo")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
