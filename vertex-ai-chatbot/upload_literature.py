
import os
import sys
import requests
import json
from pathlib import Path

def upload_literature_file(file_path, title=None, author=None, subject=None, api_url="http://localhost:8080"):    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
                filename = Path(file_path).stem
        
        data = {
            'text': content,
            'title': title or filename,
            'author': author or 'Unknown',
            'subject': subject or 'General'
        }
        
        response = requests.post(f"{api_url}/api/add-literature", json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f" Successfully uploaded: {data['title']}")
                print(f" Document ID: {result['documentId']}")
                return True
            else:
                print(f" Upload failed: {result['message']}")
                return False
        else:
            print(f" HTTP Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f" Error uploading file: {str(e)}")
        return False

def upload_directory(directory_path, subject=None, api_url="http://localhost:8080"):
    
    if not os.path.isdir(directory_path):
        print(f"Error: Directory {directory_path} does not exist")
        return
    
    text_files = []
    for ext in ['*.txt', '*.md', '*.rst']:
        text_files.extend(Path(directory_path).glob(ext))
    
    if not text_files:
        print(f"No text files found in {directory_path}")
        return
    
    print(f"Found {len(text_files)} text files to upload...")
    
    success_count = 0
    for file_path in text_files:
        if upload_literature_file(str(file_path), subject=subject, api_url=api_url):
            success_count += 1
    
    print(f"\\n Upload complete: {success_count}/{len(text_files)} files uploaded successfully")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python upload_literature.py <file_or_directory> [options]")
        print("\\nOptions:")
        print("  --title <title>      Title of the document")
        print("  --author <author>    Author of the document")
        print("  --subject <subject>  Subject category")
        print("  --api-url <url>      API URL (default: http://localhost:8080)")
        print("\\nExamples:")
        print("  python upload_literature.py ./literature/biology_textbook.txt --subject Biology")
        print("  python upload_literature.py ./literature/ --subject Physics")
        return
    
    path = sys.argv[1]
    
    title = None
    author = None
    subject = None
    api_url = "http://localhost:8080"
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--title' and i + 1 < len(sys.argv):
            title = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--author' and i + 1 < len(sys.argv):
            author = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--subject' and i + 1 < len(sys.argv):
            subject = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--api-url' and i + 1 < len(sys.argv):
            api_url = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    try:
        response = requests.get(f"{api_url}/health")
        if response.status_code != 200:
            print(f" API not available at {api_url}")
            return
    except requests.exceptions.RequestException:
        print(f" Cannot connect to API at {api_url}")
        print("   Make sure the Flask server is running")
        return
    
    if os.path.isfile(path):
        upload_literature_file(path, title, author, subject, api_url)
    elif os.path.isdir(path):
        upload_directory(path, subject, api_url)
    else:
        print(f"Error: {path} is not a valid file or directory")

if __name__ == '__main__':
    main()
