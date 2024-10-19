package com.example.myapplication

import android.annotation.SuppressLint
import android.content.Intent
import android.os.Bundle
import android.os.Environment
import android.util.Log
import android.widget.Button
import android.widget.TextView
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import java.io.File
import java.io.IOException

class chapterActivity : AppCompatActivity() {

    @SuppressLint("SetTextI18n")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_chapter)

        val chapterHeading: TextView = findViewById(R.id.ChapterHeading)
        val chapterContent: TextView = findViewById(R.id.chapterContent)

        val novel = intent.getStringExtra("novelName").toString()
        val folder = File(getExternalFilesDir(null), novel)
        var fileName = intent.getStringExtra("chapterNo").toString()
        var chapterFile = File(folder, fileName)

        if (chapterFile.exists()) {
            val fileContent = chapterFile.readText()
            val lines = fileContent.lines()
            chapterHeading.text = lines.firstOrNull() ?: "No Heading"
            val restOfContent = lines.drop(1).joinToString("\n\n")
            chapterContent.text = restOfContent
        } else {
            chapterHeading.text = "Chapter not found"
            chapterContent.text = "No content available."
        }

        val nextChapter: Button = findViewById(R.id.next)
        val prevChapter: Button = findViewById(R.id.prev)
        val homeButton: Button = findViewById(R.id.home)

        nextChapter.setOnClickListener({
            fileName = ((fileName.toIntOrNull() ?: 0) + 1).toString()
            chapterFile = File(folder, fileName)
            if (chapterFile.exists()) {
                val fileContent = chapterFile.readText()
                val lines = fileContent.lines()
                chapterHeading.text = lines.firstOrNull() ?: "No Heading"
                val restOfContent = lines.drop(1).joinToString("\n\n")
                chapterContent.text = restOfContent
                writeToContinueFile(fileName, novel)
            } else {
                chapterHeading.text = "Chapter not found"
                chapterContent.text = "No content available."
            }
        })

        prevChapter.setOnClickListener({
            fileName = ((fileName.toIntOrNull() ?: 0) - 1).toString()
            chapterFile = File(folder, fileName)
            if (chapterFile.exists()) {
                val fileContent = chapterFile.readText()
                val lines = fileContent.lines()
                chapterHeading.text = lines.firstOrNull() ?: "No Heading"
                val restOfContent = lines.drop(1).joinToString("\n\n")
                chapterContent.text = restOfContent
                writeToContinueFile(fileName, novel)
            } else {
                chapterHeading.text = "Chapter not found"
                chapterContent.text = "No content available."
            }
        })

        homeButton.setOnClickListener({
            val intent = Intent(this, novelActivity::class.java)
            intent.putExtra("novelName", novel)
            startActivity(intent)
        })
    }
    @SuppressLint("SetTextI18n")
    fun writeToContinueFile(content: String, novel: String) {
        val externalStorageDir: File = getExternalFilesDir(null) ?: Environment.getExternalStorageDirectory()
        val novelFolder = File(externalStorageDir, novel)
        val continueFile = File(novelFolder, "continue")

        try {
            continueFile.writeText(content)
        } catch (e: IOException) {
            Log.d("IO Error", e.toString())
        }
    }
}