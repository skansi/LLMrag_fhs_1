"""
Student Email Chatbot with Vector Database

A comprehensive chatbot system that uses OpenAI API and vector similarity search
to answer student emails based on uploaded documents.
"""

import os
import openai
import numpy as np
import pickle
import json
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import hashlib
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document with its metadata."""
    id: str
    content: str
    source_file: str
    chunk_index: int
    embedding: Optional[np.ndarray] = None
    metadata: Optional[Dict] = None


class VectorDatabase:
    """Vector database for storing and retrieving document embeddings."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the vector database.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model = SentenceTransformer(model_name)
        self.chunks: List[DocumentChunk] = []
        self.embeddings_matrix: Optional[np.ndarray] = None
        self.db_path = "vector_db.pkl"
        
    def add_document(self, content: str, source_file: str, 
                    chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """
        Add a document to the vector database by chunking and embedding it.
        
        Args:
            content: Text content of the document
            source_file: Name/path of the source file
            chunk_size: Size of text chunks in characters
            overlap: Overlap between chunks in characters
            
        Returns:
            List of chunk IDs that were added
        """
        # Clean and preprocess text
        content = self._preprocess_text(content)
        
        # Split into chunks
        chunks = self._chunk_text(content, chunk_size, overlap)
        
        # Create embeddings for chunks
        chunk_ids = []
        embeddings = self.model.encode(chunks)
        
        for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = self._generate_chunk_id(chunk_text, source_file, i)
            
            document_chunk = DocumentChunk(
                id=chunk_id,
                content=chunk_text,
                source_file=source_file,
                chunk_index=i,
                embedding=embedding,
                metadata={
                    "created_at": datetime.now().isoformat(),
                    "chunk_size": len(chunk_text)
                }
            )
            
            self.chunks.append(document_chunk)
            chunk_ids.append(chunk_id)
        
        # Rebuild embeddings matrix
        self._rebuild_embeddings_matrix()
        
        logger.info(f"Added {len(chunks)} chunks from {source_file}")
        return chunk_ids
    
    def search_similar(self, query: str, top_k: int = 5, 
                      min_similarity: float = 0.3) -> List[Tuple[DocumentChunk, float]]:
        """
        Search for similar document chunks based on query.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of tuples (DocumentChunk, similarity_score)
        """
        if not self.chunks or self.embeddings_matrix is None:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_embedding, self.embeddings_matrix)[0]
        
        # Get top-k similar chunks
        indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in indices:
            similarity = similarities[idx]
            if similarity >= min_similarity:
                results.append((self.chunks[idx], similarity))
        
        return results
    
    def save_database(self, filepath: Optional[str] = None) -> bool:
        """Save the vector database to disk."""
        try:
            save_path = filepath or self.db_path
            with open(save_path, 'wb') as f:
                pickle.dump({
                    'chunks': self.chunks,
                    'embeddings_matrix': self.embeddings_matrix,
                    'model_name': self.model.get_sentence_embedding_dimension()
                }, f)
            logger.info(f"Database saved to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save database: {e}")
            return False
    
    def load_database(self, filepath: Optional[str] = None) -> bool:
        """Load the vector database from disk."""
        try:
            load_path = filepath or self.db_path
            if not os.path.exists(load_path):
                logger.warning(f"Database file not found: {load_path}")
                return False
                
            with open(load_path, 'rb') as f:
                data = pickle.load(f)
                self.chunks = data['chunks']
                self.embeddings_matrix = data['embeddings_matrix']
            
            logger.info(f"Database loaded from {load_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load database: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        return {
            "total_chunks": len(self.chunks),
            "total_documents": len(set(chunk.source_file for chunk in self.chunks)),
            "embedding_dimension": self.model.get_sentence_embedding_dimension(),
            "memory_usage_mb": self.embeddings_matrix.nbytes / (1024 * 1024) if self.embeddings_matrix is not None else 0
        }
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:]', ' ', text)
        return text
    
    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at word boundaries
            if end < len(text):
                last_space = chunk.rfind(' ')
                if last_space > chunk_size // 2:
                    chunk = chunk[:last_space]
                    end = start + last_space
            
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
        return [chunk for chunk in chunks if len(chunk.strip()) > 50]
    
    def _generate_chunk_id(self, content: str, source_file: str, index: int) -> str:
        """Generate unique ID for a chunk."""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{source_file}_{index}_{content_hash}"
    
    def _rebuild_embeddings_matrix(self):
        """Rebuild the embeddings matrix from all chunks."""
        if self.chunks:
            embeddings = [chunk.embedding for chunk in self.chunks]
            self.embeddings_matrix = np.vstack(embeddings)


class StudentEmailChatbot:
    """OpenAI-powered chatbot for answering student emails."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize the chatbot.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use
        """
        openai.api_key = api_key
        self.model = model
        self.vector_db = VectorDatabase()
        self.conversation_history = []
        
        # Load existing database if available
        self.vector_db.load_database()
    
    def upload_document(self, filepath: str) -> bool:
        """
        Upload a document to the vector database.
        
        Args:
            filepath: Path to the document file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read file content based on extension
            content = self._read_document(filepath)
            
            # Add to vector database
            chunk_ids = self.vector_db.add_document(
                content=content,
                source_file=os.path.basename(filepath)
            )
            
            # Save database
            self.vector_db.save_database()
            
            logger.info(f"Successfully uploaded {filepath} with {len(chunk_ids)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload document {filepath}: {e}")
            return False
    
    def answer_email(self, email_content: str, use_context: bool = True) -> str:
        """
        Generate an answer to a student email.
        
        Args:
            email_content: The student's email content
            use_context: Whether to use vector database context
            
        Returns:
            str: Generated response
        """
        try:
            # Extract question from email
            question = self._extract_question(email_content)
            
            # Get relevant context from vector database
            context_chunks = []
            if use_context and question:
                similar_chunks = self.vector_db.search_similar(question, top_k=3)
                context_chunks = [chunk.content for chunk, score in similar_chunks]
            
            # Prepare prompt
            prompt = self._build_prompt(email_content, question, context_chunks)
            
            # Generate response using OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Store in conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "email": email_content,
                "question": question,
                "answer": answer,
                "context_used": len(context_chunks) > 0
            })
            
            return answer
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again later or contact support directly."
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get vector database statistics."""
        return self.vector_db.get_stats()
    
    def _read_document(self, filepath: str) -> str:
        """Read document content based on file extension."""
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        else:
            # For other formats, try reading as text
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                with open(filepath, 'r', encoding='latin-1') as f:
                    return f.read()
    
    def _extract_question(self, email_content: str) -> str:
        """Extract the main question from email content."""
        # Simple heuristic: look for question marks or common question patterns
        sentences = re.split(r'[.!?]+', email_content)
        questions = [s.strip() for s in sentences if '?' in s or 
                    any(word in s.lower() for word in ['how', 'what', 'when', 'where', 'why', 'can', 'could', 'would'])]
        
        if questions:
            return questions[0]
        
        # If no clear question, return first significant sentence
        significant_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        return significant_sentences[0] if significant_sentences else email_content[:200]
    
    def _build_prompt(self, email_content: str, question: str, context_chunks: List[str]) -> str:
        """Build the prompt for OpenAI."""
        prompt = f"Student Email:\n{email_content}\n\n"
        
        if context_chunks:
            prompt += "Relevant Information from Documents:\n"
            for i, chunk in enumerate(context_chunks, 1):
                prompt += f"{i}. {chunk}\n\n"
        
        prompt += "Please provide a helpful, professional response to this student email. "
        prompt += "Use the relevant information provided above when applicable. "
        prompt += "Be concise but thorough, and maintain a friendly, supportive tone."
        
        return prompt
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the chatbot."""
        return """You are a helpful academic assistant responding to student emails. 

Your responsibilities:
- Answer student questions clearly and professionally
- Use provided context from documents when relevant
- Be supportive and encouraging
- Provide actionable advice when possible
- If you don't know something, be honest about it
- Keep responses concise but informative
- Maintain a friendly, professional tone

Always structure your responses with:
1. A greeting acknowledging their question
2. The main answer/information
3. Any additional helpful resources or next steps
4. A professional closing"""


def demo_chatbot():
    """Demonstrate the chatbot functionality."""
    print("=== Student Email Chatbot Demo ===\n")
    
    # Note: You'll need to set your OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set your OPENAI_API_KEY environment variable")
        return
    
    # Initialize chatbot
    chatbot = StudentEmailChatbot(api_key)
    
    # Create sample documents
    sample_doc1 = """
    Course Syllabus - Computer Science 101
    
    Office Hours: Mondays and Wednesdays 2-4 PM
    Email: professor@university.edu
    
    Assignment Policy:
    - Assignments are due by 11:59 PM on the specified date
    - Late submissions lose 10% per day
    - Extensions may be granted for documented emergencies
    
    Grading:
    - Assignments: 40%
    - Midterm: 30%
    - Final: 30%
    
    Academic Integrity:
    Students must complete all work independently unless otherwise specified.
    Collaboration is allowed on homework but not on exams.
    """
    
    # Save sample document and upload it
    with open("sample_syllabus.txt", "w") as f:
        f.write(sample_doc1)
    
    print("1. Uploading sample documents...")
    success = chatbot.upload_document("sample_syllabus.txt")
    print(f"   Upload successful: {success}")
    
    # Show database stats
    stats = chatbot.get_database_stats()
    print(f"\n2. Database stats: {stats}")
    
    # Sample student emails
    student_emails = [
        "Hi Professor, I'm wondering what your office hours are? I need help with the assignment. Thanks!",
        "Hello, I had a family emergency and couldn't submit my assignment on time. Can I get an extension?",
        "What percentage of the grade is the final exam? I want to plan my study schedule.",
    ]
    
    print("\n3. Answering student emails:")
    for i, email in enumerate(student_emails, 1):
        print(f"\n--- Email {i} ---")
        print(f"Student: {email}")
        
        # Note: This would use actual OpenAI API in real usage
        print("Bot: [OpenAI API response would appear here]")
        print("(Set OPENAI_API_KEY environment variable to test with real API)")
    
    # Cleanup
    try:
        os.remove("sample_syllabus.txt")
        print("\n4. Cleaned up demo files")
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    demo_chatbot()
