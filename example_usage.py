import os
from dotenv import load_dotenv
from student_email_chatbot import StudentEmailChatbot
load_dotenv()
def main():
    print("=== Student Email Chatbot Example ===\n")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: Please set your OPENAI_API_KEY in a .env file")
        print("Copy .env.example to .env and add your API key")
        return
    
    print("Initializing chatbot...")
    chatbot = StudentEmailChatbot(api_key)
    print("\n1. Upload documents to vector database:")
    sample_documents = [
        "course_syllabus.txt",
        "assignment_guidelines.txt", 
        "grading_policy.txt",
        "office_hours.txt"
    ]
    for doc in sample_documents:
        if os.path.exists(doc):
            success = chatbot.upload_document(doc)
            print(f"   {doc}: {'✓' if success else '✗'}")
        else:
            print(f"   {doc}: File not found (skipping)")
    
    stats = chatbot.get_database_stats()
    print(f"\n2. Vector Database Stats:")
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Memory usage: {stats['memory_usage_mb']:.2f} MB")
    
    student_emails = [
        {
            "subject": "Question about assignment deadline",
            "content": "Hi Professor, I'm having trouble with the programming assignment. What's the deadline and is there any extension policy? Thanks!"
        },
        {
            "subject": "Office hours inquiry", 
            "content": "Hello, I'd like to know when your office hours are. I need help understanding the grading criteria for the project."
        },
        {
            "subject": "Late submission question",
            "content": "Dear Professor, I had a medical emergency and couldn't submit my assignment on time. What should I do? Can I still submit it?"
        }
    ]
    
    print(f"Processing student emails:")
    
    for i, email in enumerate(student_emails, 1):
        print(f"\n--- Email {i}: {email['subject']} ---")
        print(f"Student: {email['content']}")
        print("\nBot Response:")
        
        try:
            response = chatbot.answer_email(email['content'])
            print(response)
        except Exception as e:
            print(f"Error generating response: {e}")
        
        print("-" * 50)
    
    print(f"\nProcessed {len(student_emails)} emails successfully!")


def create_sample_documents():
    documents = {
        "course_syllabus.txt": """
        Computer Science 101 - Introduction to Programming
        
        Instructor: Dr. Smith
        Email: dr.smith@university.edu
        Office: Room 301, Computer Science Building
        Office Hours: Mondays and Wednesdays, 2:00-4:00 PM
        
        Course Description:
        This course introduces fundamental programming concepts using Python.
        
        Grading Policy:
        - Programming Assignments: 40%
        - Midterm Exam: 25%
        - Final Project: 25%
        - Participation: 10%
        
        Late Policy:
        Assignments submitted late will lose 10% per day, up to 3 days.
        After 3 days, no credit will be given unless there are documented
        extenuating circumstances.
        """,
        
        "assignment_guidelines.txt": """
        Programming Assignment Guidelines
        
        Submission Requirements:
        1. All code must be well-commented
        2. Follow Python PEP 8 style guidelines
        3. Include a README file with your submission
        4. Test your code thoroughly before submission
        
        File Naming Convention:
        - Use your student ID in the filename
        - Example: assignment1_12345678.py
        
        Academic Integrity:
        - All work must be your own
        - You may discuss concepts with classmates
        - Do not share code or copy from others
        - Cite any external resources used
        
        Getting Help:
        - Attend office hours for one-on-one help
        - Use the course discussion forum
        - Email the instructor for urgent questions
        """,
        
        "grading_policy.txt": """
        Detailed Grading Policy
        
        Programming Assignments (40%):
        - Correctness: 60%
        - Code Quality: 25%
        - Documentation: 15%
        
        Exams (50% total):
        - Midterm: 25%
        - Final: 25%
        
        Participation (10%):
        - Class attendance
        - Discussion forum contributions
        - Peer help and collaboration
        
        Grade Scale:
        A: 90-100%
        B: 80-89%
        C: 70-79%
        D: 60-69%
        F: Below 60%
        
        Extra Credit:
        Optional extra credit assignments may be offered
        throughout the semester for up to 5% additional points.
        """
    }
    
    print("Creating sample documents...")
    for filename, content in documents.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"Created: {filename}")


if __name__ == "__main__":
    # create_sample_documents()
    
    main()
