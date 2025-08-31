package com.studentnotes.ocrscanner

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import android.Manifest
import android.content.pm.PackageManager
import android.widget.Toast
import com.studentnotes.ocrscanner.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    private val CAMERA_PERMISSION_REQUEST_CODE = 1001
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupClickListeners()
        checkCameraPermission()
    }
    
    private fun setupClickListeners() {
        binding.btnScanNotes.setOnClickListener {
            if (checkCameraPermission()) {
                startCameraActivity()
            } else {
                requestCameraPermission()
            }
        }
        
        binding.btnViewHistory.setOnClickListener {
            // TODO: Implement view history functionality
            Toast.makeText(this, "History feature coming soon!", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun checkCameraPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.CAMERA
        ) == PackageManager.PERMISSION_GRANTED
    }
    
    private fun requestCameraPermission() {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(Manifest.permission.CAMERA),
            CAMERA_PERMISSION_REQUEST_CODE
        )
    }
    
    private fun startCameraActivity() {
        val intent = Intent(this, CameraActivity::class.java)
        startActivity(intent)
    }
    
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        when (requestCode) {
            CAMERA_PERMISSION_REQUEST_CODE -> {
                if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    startCameraActivity()
                } else {
                    Toast.makeText(
                        this,
                        "Camera permission is required to scan notes",
                        Toast.LENGTH_LONG
                    ).show()
                }
            }
        }
    }
}
