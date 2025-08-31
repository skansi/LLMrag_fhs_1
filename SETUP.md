# Student Notes AI System - Setup Guide

## 🎯 Quick Overview

This system consists of:
1. **Android App** - Scans handwritten notes using OCR
2. **Python Backend** - AI-powered note completion using Google Vertex AI
3. **Vector Database** - Stores academic literature for contextual enhancement

## 🚀 Quick Start (5 Minutes)

### Step 1: Backend Setup
```bash
# Navigate to backend directory
cd vertex-ai-chatbot

# Install Python dependencies
pip install -r requirements.txt

# Set up Google Cloud authentication
gcloud auth application-default login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Copy environment file and configure
cp .env.example .env
# Edit .env with your project details

# Start the backend server
python app.py
```

### Step 2: Test the Backend
```bash
# Run API tests
python test_api.py
```

### Step 3: Android App Setup
1. Open `android-ocr-app` in Android Studio
2. Update the API URL in network configuration
3. Build and run on Android device/emulator

### Step 4: Upload Literature (Optional)
```bash
# Upload academic documents to enhance AI responses
python upload_literature.py ./documents/textbook.txt --subject Biology
```

## 📱 Android App Features

### Main Screen
- **Scan Notes** - Opens camera for note capture
- **View History** - Access previously processed notes

### Camera Screen
- Live camera preview with overlay frame
- Tap to capture handwritten notes
- Optimized for document scanning

### OCR Processing Screen
- Real-time text extraction using Google ML Kit
- Edit extracted text before AI processing
- Preview captured image

### Results Screen
- AI-enhanced note completion
- Share completed notes
- Start new scanning session

## 🤖 Backend API Features

### Core Endpoints

#### Health Check
```http
GET /health
```

#### Upload Text from Android
```http
POST /api/upload-text
{
  "text": "extracted handwritten content",
  "fileName": "notes_2024.txt",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Complete Notes with AI
```http
POST /api/complete-notes
{
  "extractedText": "photosynthesis - plants use light",
  "subject": "Biology"
}
```

#### Add Academic Literature
```http
POST /api/add-literature
{
  "text": "academic content here...",
  "title": "Introduction to Biology",
  "author": "Dr. Smith",
  "subject": "Biology"
}
```

#### Search Literature Database
```http
POST /api/search-literature
{
  "query": "photosynthesis chlorophyll",
  "n_results": 5
}
```

## 🛠 Configuration

### Google Cloud Setup
1. Create a Google Cloud project
2. Enable required APIs:
   - Vertex AI API
   - Cloud Storage API
   - Cloud Run API (for deployment)
3. Set up authentication
4. Configure billing

### Environment Variables (`.env`)
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
STORAGE_BUCKET=your-bucket-name
CHROMA_DB_PATH=./chroma_db
MODEL_NAME=text-bison@001
MAX_OUTPUT_TOKENS=1024
TEMPERATURE=0.3
```

### Android Configuration
Update in `ChatbotService.kt`:
```kotlin
private const val BASE_URL = "http://your-backend-url"
```

## 📚 How It Works

### 1. Note Scanning Flow
```
Android Camera → Image Capture → ML Kit OCR → Text Extraction → Backend API
```

### 2. AI Enhancement Flow
```
Extracted Text → Vector DB Query → Vertex AI Processing → Enhanced Notes
```

### 3. Literature Integration
```
Academic Documents → ChromaDB Vectors → Contextual Search → AI Enhancement
```

## 🚀 Deployment Options

### Local Development
- Run Python backend locally
- Connect Android app to local server
- Use SQLite ChromaDB storage

### Cloud Deployment
```bash
# Quick cloud deployment
./deploy.ps1  # Windows
./deploy.sh   # Linux/Mac
```

### Production Deployment
- Deploy backend to Google Cloud Run
- Use Cloud Storage for file management
- Configure proper authentication and security

## 🧪 Testing

### Backend Testing
```bash
cd vertex-ai-chatbot
python test_api.py
```

### Android Testing
- Use Android Studio emulator
- Test camera permissions
- Verify OCR functionality
- Test API connectivity

## 📖 Usage Examples

### Example 1: Biology Notes
**Input (Handwritten):** "Photosynthesis - plants use sunlight"

**AI Output:**
```
# Photosynthesis - Complete Notes

## Overview
Photosynthesis is the process by which plants convert sunlight into chemical energy.

## Key Components
- **Chlorophyll**: Green pigment that captures light energy
- **Sunlight**: Primary energy source
- **Carbon Dioxide**: Input from atmosphere
- **Water**: Input from roots

## Chemical Equation
6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂

## Further Reading
[Based on literature database queries]
```

### Example 2: Math Notes
**Input:** "Integration by parts"

**AI Output:**
- Complete formula derivation
- Step-by-step examples
- Common applications
- Practice problems

## 🔧 Troubleshooting

### Common Issues

1. **OCR Not Working**
   - Check Google Play Services
   - Verify camera permissions
   - Ensure good lighting

2. **API Connection Failed**
   - Verify backend is running
   - Check network connectivity
   - Validate API endpoints

3. **AI Processing Errors**
   - Confirm Google Cloud authentication
   - Check Vertex AI API limits
   - Verify project configuration

4. **Vector Database Issues**
   - Ensure ChromaDB directory exists
   - Check file permissions
   - Verify literature upload

### Debug Commands
```bash
# Check backend status
curl http://localhost:8080/health

# Test specific endpoint
curl -X POST http://localhost:8080/api/complete-notes \
  -H "Content-Type: application/json" \
  -d '{"extractedText": "test note"}'

# View backend logs
python app.py  # Check console output
```

## 📋 Next Steps

### Immediate Actions
1. ✅ Set up Google Cloud project
2. ✅ Deploy backend service
3. ✅ Build Android app
4. ✅ Test complete workflow

### Enhancements
- Add user authentication
- Implement note categorization
- Add handwriting quality detection
- Support multiple languages
- Add collaborative features

### Production Considerations
- Implement proper security
- Add monitoring and logging
- Optimize for scale
- Add error recovery
- Implement data backup

---

**🎉 You're ready to start enhancing student notes with AI!**

For additional help, check the main README.md or open an issue on GitHub.
