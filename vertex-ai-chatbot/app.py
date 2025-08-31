from flask import Flask, request, jsonify
from google.cloud import aiplatform
from google.cloud import storage
import vertexai
from vertexai.language_models import TextGenerationModel
import chromadb
from chromadb.config import Settings
import os
import logging
from datetime import datetime
import json
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'your-project-id')
LOCATION = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
BUCKET_NAME = os.getenv('STORAGE_BUCKET', 'student-notes-storage')

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize ChromaDB for vector database
chroma_client = chromadb.PersistentClient(path="./chroma_db")
literature_collection = chroma_client.get_or_create_collection(
    name="literature_database",
    metadata={"description": "Academic literature and reference materials"}
)

class NotesCompletionService:
    def __init__(self):
        self.model = TextGenerationModel.from_pretrained("text-bison@001")
        self.storage_client = storage.Client()
        
    def upload_text_file(self, text_content, filename):
        """Upload extracted text to Google Cloud Storage"""
        try:
            bucket = self.storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob(f"extracted_texts/{filename}")
            blob.upload_from_string(text_content)
            return blob.public_url
        except Exception as e:
            logger.error(f"Failed to upload file: {str(e)}")
            return None
    
    def query_literature_database(self, text_content, n_results=5):
        """Query the vector database for relevant literature"""
        try:
            results = literature_collection.query(
                query_texts=[text_content],
                n_results=n_results
            )
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            logger.error(f"Failed to query literature database: {str(e)}")
            return []
    
    def complete_notes_with_ai(self, extracted_text, context_docs=None):
        """Use Vertex AI to complete and enhance the notes"""
        try:
            # Build context from vector database results
            context = ""
            if context_docs:
                context = "\\n\\nRelevant academic context:\\n" + "\\n".join(context_docs[:3])
            
            prompt = f"""
            You are an AI academic assistant helping students complete their handwritten notes. 
            
            Original extracted text from handwritten notes:
            {extracted_text}
            
            {context}
            
            Please:
            1. Clean up and organize the extracted text
            2. Fill in any gaps or incomplete thoughts
            3. Add relevant explanations and context
            4. Suggest related concepts and topics
            5. Provide a well-structured, comprehensive version of the notes
            6. Add section headings where appropriate
            
            Format the response as a complete set of study notes with clear sections and bullet points.
            """
            
            response = self.model.predict(
                prompt,
                temperature=0.3,
                max_output_tokens=1024,
                top_k=40,
                top_p=0.8
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Failed to complete notes with AI: {str(e)}")
            raise
    
    def add_literature_to_database(self, document_text, metadata):
        """Add academic literature to the vector database"""
        try:
            doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            literature_collection.add(
                documents=[document_text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            return doc_id
        except Exception as e:
            logger.error(f"Failed to add literature to database: {str(e)}")
            raise

# Initialize the service
notes_service = NotesCompletionService()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/upload-text', methods=['POST'])
def upload_extracted_text():
    """Endpoint to receive extracted text from Android app"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'message': 'No text provided'
            }), 400
        
        text_content = data['text']
        filename = data.get('fileName', f"notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        # Upload to cloud storage
        file_url = notes_service.upload_text_file(text_content, filename)
        
        if file_url:
            return jsonify({
                'success': True,
                'fileId': filename,
                'message': 'Text uploaded successfully',
                'url': file_url
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to upload text'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in upload_extracted_text: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/complete-notes', methods=['POST'])
def complete_notes():
    """Endpoint to complete notes using Vertex AI and vector database"""
    try:
        data = request.get_json()
        
        if not data or 'extractedText' not in data:
            return jsonify({
                'success': False,
                'error': 'No extracted text provided'
            }), 400
        
        extracted_text = data['extractedText']
        subject = data.get('subject', '')
        
        # Query vector database for relevant literature
        logger.info("Querying literature database...")
        relevant_docs = notes_service.query_literature_database(extracted_text)
        
        # Complete notes with AI
        logger.info("Completing notes with Vertex AI...")
        completed_notes = notes_service.complete_notes_with_ai(extracted_text, relevant_docs)
        
        # Prepare sources information
        sources = []
        if relevant_docs:
            sources = [f"Academic reference {i+1}" for i in range(len(relevant_docs[:3]))]
        
        return jsonify({
            'success': True,
            'completedNotes': completed_notes,
            'sources': sources,
            'originalText': extracted_text
        })
        
    except Exception as e:
        logger.error(f"Error in complete_notes: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to complete notes',
            'details': str(e)
        }), 500

@app.route('/api/add-literature', methods=['POST'])
def add_literature():
    """Endpoint to add academic literature to the vector database"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'message': 'No text provided'
            }), 400
        
        document_text = data['text']
        metadata = {
            'title': data.get('title', 'Untitled Document'),
            'author': data.get('author', 'Unknown'),
            'subject': data.get('subject', 'General'),
            'uploaded_at': datetime.now().isoformat()
        }
        
        doc_id = notes_service.add_literature_to_database(document_text, metadata)
        
        return jsonify({
            'success': True,
            'documentId': doc_id,
            'message': 'Literature added to database successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in add_literature: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to add literature',
            'error': str(e)
        }), 500

@app.route('/api/search-literature', methods=['POST'])
def search_literature():
    """Endpoint to search the literature database"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        n_results = data.get('n_results', 5)
        
        if not query:
            return jsonify({
                'success': False,
                'message': 'No search query provided'
            }), 400
        
        results = literature_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        formatted_results = []
        if results['documents'] and results['metadatas']:
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                formatted_results.append({
                    'text': doc,
                    'metadata': metadata
                })
        
        return jsonify({
            'success': True,
            'results': formatted_results,
            'count': len(formatted_results)
        })
        
    except Exception as e:
        logger.error(f"Error in search_literature: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to search literature',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
