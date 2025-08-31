#!/bin/bash

# Student Notes AI System Deployment Script

echo "🚀 Student Notes AI System Deployment"
echo "======================================"

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if gcloud CLI is installed
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud CLI is not installed"
        echo "Please install it from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    print_status "Google Cloud CLI found"
}

# Check if project ID is set
check_project() {
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$PROJECT_ID" ]; then
        print_error "No Google Cloud project set"
        echo "Please run: gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
    print_status "Using project: $PROJECT_ID"
}

# Enable required APIs
enable_apis() {
    print_status "Enabling required Google Cloud APIs..."
    
    gcloud services enable aiplatform.googleapis.com --quiet
    gcloud services enable storage.googleapis.com --quiet
    gcloud services enable run.googleapis.com --quiet
    
    print_status "APIs enabled successfully"
}

# Create storage bucket
create_bucket() {
    BUCKET_NAME="${PROJECT_ID}-student-notes"
    
    if gsutil ls -b gs://$BUCKET_NAME &> /dev/null; then
        print_status "Storage bucket already exists: $BUCKET_NAME"
    else
        print_status "Creating storage bucket: $BUCKET_NAME"
        gsutil mb gs://$BUCKET_NAME
        print_status "Storage bucket created successfully"
    fi
    
    echo "STORAGE_BUCKET=$BUCKET_NAME" >> .env
}

# Deploy to Cloud Run
deploy_backend() {
    print_status "Deploying backend to Cloud Run..."
    
    cd vertex-ai-chatbot
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        cp .env.example .env
        sed -i "s/your-project-id/$PROJECT_ID/g" .env
        sed -i "s/student-notes-storage/${PROJECT_ID}-student-notes/g" .env
    fi
    
    # Deploy to Cloud Run
    gcloud run deploy student-notes-ai \\
        --source . \\
        --platform managed \\
        --region us-central1 \\
        --allow-unauthenticated \\
        --memory 2Gi \\
        --cpu 2 \\
        --timeout 300 \\
        --quiet
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe student-notes-ai --region=us-central1 --format='value(status.url)')
    
    print_status "Backend deployed successfully"
    echo "Service URL: $SERVICE_URL"
    
    cd ..
}

# Test the deployment
test_deployment() {
    print_status "Testing deployment..."
    
    cd vertex-ai-chatbot
    
    # Update test script to use Cloud Run URL
    if [ ! -z "$SERVICE_URL" ]; then
        sed -i "s|http://localhost:8080|$SERVICE_URL|g" test_api.py
        python test_api.py
    else
        print_warning "Could not determine service URL for testing"
    fi
    
    cd ..
}

# Setup Android app configuration
setup_android() {
    print_status "Setting up Android app configuration..."
    
    if [ ! -z "$SERVICE_URL" ]; then
        echo "Update the following in your Android app:"
        echo "- BASE_URL in network service: $SERVICE_URL"
        echo "- Update ChatbotService.kt with the correct endpoint"
        
        # Create a config file for Android
        cat > android-ocr-app/api_config.txt << EOF
# API Configuration for Android App
# Update these values in your Android app

BASE_URL = "$SERVICE_URL"

# Update in ChatbotService.kt:
# private const val BASE_URL = "$SERVICE_URL"
EOF
        
        print_status "API configuration saved to android-ocr-app/api_config.txt"
    else
        print_warning "Service URL not available for Android configuration"
    fi
}

# Main deployment flow
main() {
    echo "Starting deployment process..."
    echo
    
    check_gcloud
    check_project
    enable_apis
    create_bucket
    deploy_backend
    test_deployment
    setup_android
    
    echo
    print_status "Deployment completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Update Android app with the API URL from android-ocr-app/api_config.txt"
    echo "2. Build and test the Android app"
    echo "3. Upload literature using: python vertex-ai-chatbot/upload_literature.py"
    echo "4. Test the complete system"
    echo
    echo "Service URL: $SERVICE_URL"
}

# Run the deployment
main
