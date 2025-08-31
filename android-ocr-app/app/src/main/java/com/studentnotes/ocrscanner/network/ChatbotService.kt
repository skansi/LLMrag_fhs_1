package com.studentnotes.ocrscanner.network

import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.POST

interface ChatbotService {
    
    @POST("api/complete-notes")
    fun completeNotes(@Body request: CompletionRequest): Call<CompletionResponse>
    
    @POST("api/upload-text")
    fun uploadExtractedText(@Body request: TextUploadRequest): Call<TextUploadResponse>
}

data class CompletionRequest(
    val extractedText: String,
    val subject: String? = null,
    val context: String? = null
)

data class CompletionResponse(
    val success: Boolean,
    val completedNotes: String,
    val sources: List<String>? = null,
    val error: String? = null
)

data class TextUploadRequest(
    val text: String,
    val timestamp: String,
    val fileName: String
)

data class TextUploadResponse(
    val success: Boolean,
    val fileId: String? = null,
    val message: String
)
