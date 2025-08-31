package com.studentnotes.ocrscanner

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.studentnotes.ocrscanner.databinding.ActivityResultBinding
import com.studentnotes.ocrscanner.network.ChatbotService
import com.studentnotes.ocrscanner.network.CompletionRequest
import com.studentnotes.ocrscanner.network.CompletionResponse
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class ResultActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityResultBinding
    private var extractedText: String = ""
    private var textFilePath: String = ""
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityResultBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        extractedText = intent.getStringExtra("extracted_text") ?: ""
        textFilePath = intent.getStringExtra("text_file_path") ?: ""
        
        binding.tvExtractedText.text = extractedText
        
        setupClickListeners()
    }
    
    private fun setupClickListeners() {
        binding.btnCompleteNotes.setOnClickListener {
            completeNotesWithChatbot()
        }
        
        binding.btnStartNew.setOnClickListener {
            val intent = Intent(this, MainActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
            startActivity(intent)
            finish()
        }
        
        binding.btnShareNotes.setOnClickListener {
            shareNotes()
        }
    }
    
    private fun completeNotesWithChatbot() {
        binding.progressBar.visibility = View.VISIBLE
        binding.tvStatus.text = "Connecting to AI chatbot..."
        
        // In a real implementation, you would send this to your backend service
        // For demonstration, we'll simulate the API call
        simulateChatbotCompletion()
    }
    
    private fun simulateChatbotCompletion() {
        // This simulates calling your Python backend with Vertex AI
        binding.tvStatus.text = "AI is analyzing and completing your notes..."
        
        // Simulate processing time
        binding.root.postDelayed({
            binding.progressBar.visibility = View.GONE
            
            val completedNotes = """
                ${extractedText}
                
                ## AI-Generated Completion:
                
                Based on your handwritten notes, here are some key points and expansions:
                
                • [AI would analyze the content and provide relevant context]
                • [Additional explanations based on vector database queries]
                • [Related concepts and references from academic literature]
                • [Clarifications and examples to enhance understanding]
                
                ## Suggested Further Reading:
                • [AI-recommended resources based on vector database]
                • [Related academic papers and references]
                
                Note: This is a demonstration. In the full implementation, 
                this would be powered by Google Vertex AI and a comprehensive vector database.
            """.trimIndent()
            
            binding.tvCompletedNotes.text = completedNotes
            binding.tvCompletedNotes.visibility = View.VISIBLE
            binding.tvStatus.text = "Notes completed successfully!"
            
        }, 3000) // 3 second delay to simulate processing
    }
    
    private fun shareNotes() {
        val shareText = if (binding.tvCompletedNotes.visibility == View.VISIBLE) {
            binding.tvCompletedNotes.text.toString()
        } else {
            extractedText
        }
        
        val shareIntent = Intent().apply {
            action = Intent.ACTION_SEND
            putExtra(Intent.EXTRA_TEXT, shareText)
            type = "text/plain"
        }
        
        startActivity(Intent.createChooser(shareIntent, "Share Notes"))
    }
    
    companion object {
        private const val TAG = "ResultActivity"
    }
}
