package com.studentnotes.ocrscanner

import android.content.Intent
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import com.studentnotes.ocrscanner.databinding.ActivityOcrprocessingBinding
import java.io.File
import java.io.FileWriter
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.*

class OCRProcessingActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityOcrprocessingBinding
    private var imagePath: String? = null
    private var extractedText: String = ""
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityOcrprocessingBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        imagePath = intent.getStringExtra("image_path")
        
        if (imagePath != null) {
            displayImage()
            processImageWithOCR()
        } else {
            Toast.makeText(this, "Error: No image to process", Toast.LENGTH_LONG).show()
            finish()
        }
        
        setupClickListeners()
    }
    
    private fun setupClickListeners() {
        binding.btnRetake.setOnClickListener {
            finish()
        }
        
        binding.btnSendToChatbot.setOnClickListener {
            if (extractedText.isNotEmpty()) {
                saveAndSendText()
            } else {
                Toast.makeText(this, "No text extracted yet", Toast.LENGTH_SHORT).show()
            }
        }
        
        binding.btnEditText.setOnClickListener {
            binding.etExtractedText.isEnabled = !binding.etExtractedText.isEnabled
            if (binding.etExtractedText.isEnabled) {
                binding.btnEditText.text = "Done Editing"
            } else {
                binding.btnEditText.text = "Edit Text"
                extractedText = binding.etExtractedText.text.toString()
            }
        }
    }
    
    private fun displayImage() {
        imagePath?.let { path ->
            val bitmap = BitmapFactory.decodeFile(path)
            binding.ivCapturedImage.setImageBitmap(bitmap)
        }
    }
    
    private fun processImageWithOCR() {
        binding.progressBar.visibility = View.VISIBLE
        binding.tvStatus.text = "Processing image with OCR..."
        
        imagePath?.let { path ->
            val image = InputImage.fromFilePath(this, Uri.fromFile(File(path)))
            val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
            
            recognizer.process(image)
                .addOnSuccessListener { visionText ->
                    binding.progressBar.visibility = View.GONE
                    extractedText = visionText.text
                    
                    if (extractedText.isNotEmpty()) {
                        binding.etExtractedText.setText(extractedText)
                        binding.tvStatus.text = "Text extracted successfully!"
                        binding.btnSendToChatbot.isEnabled = true
                    } else {
                        binding.tvStatus.text = "No text found in image"
                        binding.etExtractedText.setText("No text detected. You can manually type the notes here.")
                    }
                }
                .addOnFailureListener { e ->
                    binding.progressBar.visibility = View.GONE
                    binding.tvStatus.text = "OCR processing failed"
                    Log.e(TAG, "Text recognition failed", e)
                    Toast.makeText(this, "OCR processing failed: ${e.message}", Toast.LENGTH_LONG).show()
                }
        }
    }
    
    private fun saveAndSendText() {
        val timestamp = SimpleDateFormat("yyyy-MM-dd_HH-mm-ss", Locale.US).format(Date())
        val fileName = "notes_$timestamp.txt"
        val file = File(getExternalFilesDir(null), fileName)
        
        try {
            FileWriter(file).use { writer ->
                writer.write("# Student Notes - Extracted on $timestamp\n\n")
                writer.write(extractedText)
                writer.write("\n\n# End of extracted notes")
            }
            
            // Here you would typically send the file to your chatbot service
            // For now, we'll show a success message and navigate to results
            val intent = Intent(this, ResultActivity::class.java)
            intent.putExtra("text_file_path", file.absolutePath)
            intent.putExtra("extracted_text", extractedText)
            startActivity(intent)
            
        } catch (e: IOException) {
            Log.e(TAG, "Failed to save text file", e)
            Toast.makeText(this, "Failed to save text file", Toast.LENGTH_LONG).show()
        }
    }
    
    companion object {
        private const val TAG = "OCRProcessingActivity"
    }
}
