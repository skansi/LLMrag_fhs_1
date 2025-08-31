# Student Notes AI System Deployment Script (PowerShell)

Write-Host "🚀 Student Notes AI System Deployment" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Function to print colored output
function Write-Status {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# Check if gcloud CLI is installed
function Test-GCloud {
    try {
        $null = Get-Command gcloud -ErrorAction Stop
        Write-Status "Google Cloud CLI found"
        return $true
    }
    catch {
        Write-Error "Google Cloud CLI is not installed"
        Write-Host "Please install it from: https://cloud.google.com/sdk/docs/install"
        return $false
    }
}

# Check if project ID is set
function Test-Project {
    $projectId = gcloud config get-value project 2>$null
    if ([string]::IsNullOrEmpty($projectId)) {
        Write-Error "No Google Cloud project set"
        Write-Host "Please run: gcloud config set project YOUR_PROJECT_ID"
        return $false
    }
    Write-Status "Using project: $projectId"
    return $projectId
}

# Enable required APIs
function Enable-APIs {
    Write-Status "Enabling required Google Cloud APIs..."
    
    gcloud services enable aiplatform.googleapis.com --quiet
    gcloud services enable storage.googleapis.com --quiet
    gcloud services enable run.googleapis.com --quiet
    
    Write-Status "APIs enabled successfully"
}

# Create storage bucket
function New-StorageBucket {
    param($ProjectId)
    
    $bucketName = "$ProjectId-student-notes"
    
    $bucketExists = gsutil ls -b "gs://$bucketName" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Status "Storage bucket already exists: $bucketName"
    }
    else {
        Write-Status "Creating storage bucket: $bucketName"
        gsutil mb "gs://$bucketName"
        Write-Status "Storage bucket created successfully"
    }
    
    Add-Content -Path ".env" -Value "STORAGE_BUCKET=$bucketName"
    return $bucketName
}

# Deploy to Cloud Run
function Deploy-Backend {
    param($ProjectId)
    
    Write-Status "Deploying backend to Cloud Run..."
    
    Push-Location "vertex-ai-chatbot"
    
    # Create .env file if it doesn't exist
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
        (Get-Content ".env") -replace "your-project-id", $ProjectId | Set-Content ".env"
        (Get-Content ".env") -replace "student-notes-storage", "$ProjectId-student-notes" | Set-Content ".env"
    }
    
    # Deploy to Cloud Run
    gcloud run deploy student-notes-ai `
        --source . `
        --platform managed `
        --region us-central1 `
        --allow-unauthenticated `
        --memory 2Gi `
        --cpu 2 `
        --timeout 300 `
        --quiet
    
    # Get the service URL
    $serviceUrl = gcloud run services describe student-notes-ai --region=us-central1 --format='value(status.url)'
    
    Write-Status "Backend deployed successfully"
    Write-Host "Service URL: $serviceUrl"
    
    Pop-Location
    return $serviceUrl
}

# Test the deployment
function Test-Deployment {
    param($ServiceUrl)
    
    Write-Status "Testing deployment..."
    
    Push-Location "vertex-ai-chatbot"
    
    # Update test script to use Cloud Run URL
    if (![string]::IsNullOrEmpty($ServiceUrl)) {
        (Get-Content "test_api.py") -replace "http://localhost:8080", $ServiceUrl | Set-Content "test_api.py"
        python test_api.py
    }
    else {
        Write-Warning "Could not determine service URL for testing"
    }
    
    Pop-Location
}

# Setup Android app configuration
function Set-AndroidConfig {
    param($ServiceUrl)
    
    Write-Status "Setting up Android app configuration..."
    
    if (![string]::IsNullOrEmpty($ServiceUrl)) {
        Write-Host "Update the following in your Android app:"
        Write-Host "- BASE_URL in network service: $ServiceUrl"
        Write-Host "- Update ChatbotService.kt with the correct endpoint"
        
        # Create a config file for Android
        $configContent = @"
# API Configuration for Android App
# Update these values in your Android app

BASE_URL = "$ServiceUrl"

# Update in ChatbotService.kt:
# private const val BASE_URL = "$ServiceUrl"
"@
        
        $configContent | Out-File -FilePath "android-ocr-app\api_config.txt" -Encoding UTF8
        
        Write-Status "API configuration saved to android-ocr-app\api_config.txt"
    }
    else {
        Write-Warning "Service URL not available for Android configuration"
    }
}

# Main deployment flow
function Start-Deployment {
    Write-Host "Starting deployment process..." -ForegroundColor Cyan
    Write-Host ""
    
    if (-not (Test-GCloud)) { return }
    
    $projectId = Test-Project
    if (-not $projectId) { return }
    
    Enable-APIs
    $bucketName = New-StorageBucket -ProjectId $projectId
    $serviceUrl = Deploy-Backend -ProjectId $projectId
    Test-Deployment -ServiceUrl $serviceUrl
    Set-AndroidConfig -ServiceUrl $serviceUrl
    
    Write-Host ""
    Write-Status "Deployment completed successfully!"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Update Android app with the API URL from android-ocr-app\api_config.txt"
    Write-Host "2. Build and test the Android app"
    Write-Host "3. Upload literature using: python vertex-ai-chatbot\upload_literature.py"
    Write-Host "4. Test the complete system"
    Write-Host ""
    Write-Host "Service URL: $serviceUrl" -ForegroundColor Green
}

# Run the deployment
Start-Deployment
