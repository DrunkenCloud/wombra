package com.example.myapplication

import android.annotation.SuppressLint
import android.content.Intent
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.widget.Button
import android.widget.TextView
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import com.chaquo.python.Python
import com.google.android.material.textfield.TextInputEditText

class addNovel : AppCompatActivity() {
    @SuppressLint("SetTextI18n")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_add_novel)
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        val addNovel = findViewById<Button>(R.id.addNovelButton)
        val textInput: TextInputEditText = findViewById(R.id.inputEditText)
        val textView: TextView = findViewById(R.id.urlView)
        addNovel.setOnClickListener(){
            val url = textInput.text?.ifEmpty {
                ""
            }
            if (url != null) {
                if (url == "") {
                    return@setOnClickListener
                }
            }
            val externalStorageDir = getExternalFilesDir(null) ?: Environment.getExternalStorageDirectory()
            val py = Python.getInstance()
            val module = py.getModule("startup")
            textView.text = "Please Wait for 5 secs!"
            module.callAttr("initialise", url.toString(), externalStorageDir.absolutePath)
            val handler = Handler(Looper.getMainLooper())
            handler.postDelayed({
                val intent = Intent(this, MainActivity::class.java)
                startActivity(intent)
            }, 5000)
        }
    }
}