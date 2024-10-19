package com.example.myapplication

import android.Manifest
import android.annotation.SuppressLint
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.widget.Button
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.chaquo.python.Python
import java.io.File
import java.io.IOException
import kotlin.concurrent.thread

class novelActivity : AppCompatActivity() {
    private val permsCode = 420
    private var stopFlag = false

    @SuppressLint("SetTextI18n")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_novel)

        val downloadButton: Button = findViewById(R.id.downloadChapsButton)
        val startButton: Button = findViewById(R.id.startReading)
        val continueButton: Button = findViewById(R.id.continueReading)
        val outputText: TextView = findViewById(R.id.outputText)
        val home: Button = findViewById(R.id.homeButton)
        val novel: String = intent.getStringExtra("novelName").toString()
        val novelImage: ImageView = findViewById(R.id.novelImage)
        val novelTitle: TextView = findViewById(R.id.novelTitle)
        val externalStorageDir: File = getExternalFilesDir(null) ?: Environment.getExternalStorageDirectory()
        val novelFolder = File(externalStorageDir, novel)
        val chaptersLayout: LinearLayout = findViewById(R.id.chaptersList)
        val indexFile = File(novelFolder, "index")
        val imageFile = File(novelFolder, "image.jpg")

        outputText.text = "Novel name is $novel"
        novelTitle.text = novel.split('-').joinToString(" ") { word -> word.replaceFirstChar { it.uppercase() } }
        val imageUri = Uri.fromFile(imageFile)
        novelImage.setImageURI(imageUri)

        try {
            if (indexFile.exists()) {
                val content = indexFile.readText()
                val lines = content.lines()

                runOnUiThread {
                    lines.forEachIndexed { index, heading ->
                        val chapterNo = index + 1

                        val chapterButton = Button(this)
                        chapterButton.text = heading

                        val layoutParams = LinearLayout.LayoutParams(
                            LinearLayout.LayoutParams.MATCH_PARENT,
                            LinearLayout.LayoutParams.WRAP_CONTENT
                        )
                        layoutParams.setMargins(0, 0, 0, 0)
                        chapterButton.layoutParams = layoutParams

                        chapterButton.setOnClickListener {
                            val intent = Intent(this, chapterActivity::class.java)
                            intent.putExtra("novelName", novel)
                            intent.putExtra("chapterNo", chapterNo.toString())
                            writeToContinueFile(chapterNo.toString(), novel, outputText)
                            startActivity(intent)
                        }
                        chaptersLayout.addView(chapterButton)
                    }
                }
            }
        } catch (e: IOException) {
            runOnUiThread {
                outputText.text = "Error reading the index file: ${e.message}"
            }
        }

        startButton.setOnClickListener {
            val intent = Intent(this, chapterActivity::class.java)
            intent.putExtra("novelName", novel)
            intent.putExtra("chapterNo", "1")
            writeToContinueFile("1", novel, outputText)
            startActivity(intent)
        }

        if (!hasStoragePermission()) {
            requestStoragePermission()
        }

        var downloadThread: Thread? = null

        downloadButton.setOnClickListener {
            if (!stopFlag) {
                stopFlag = true
                downloadButton.text = "Download"
                downloadButton.setBackgroundColor(ContextCompat.getColor(this, R.color.purple_200))

                thread {
                    try {
                        val py = Python.getInstance()
                        val module = py.getModule("trial")
                        module.callAttr("stopDownload")

                        downloadThread?.interrupt()
                    } catch (e: Exception) {
                        runOnUiThread {
                            outputText.text = "Error stopping the download: ${e.message}"
                        }
                    }
                }
            } else {
                if (hasStoragePermission()) {
                    stopFlag = false
                    downloadButton.text = "CANCEL"
                    downloadButton.setBackgroundColor(ContextCompat.getColor(this, R.color.red_dik))

                    downloadThread = thread {
                        try {
                            val py = Python.getInstance()
                            val module = py.getModule("trial")

                            val stdout = { output: String ->
                                if (output.isNotBlank()) {
                                    runOnUiThread {
                                        outputText.text = output
                                    }
                                }
                            }

                            val externalStorageDir: File = getExternalFilesDir(null)
                                ?: Environment.getExternalStorageDirectory()

                            module.callAttr("downloadChapters", "https://readnovelfull.com/${novel}.html", stdout, externalStorageDir.absolutePath)

                        } catch (e: InterruptedException) {
                            runOnUiThread {
                                outputText.text = "Download interrupted."
                            }
                        } catch (e: Exception) {
                            runOnUiThread {
                                outputText.text = "Error: ${e.message}"
                            }
                        } finally {
                            runOnUiThread {
                                downloadButton.text = "Download"
                                downloadButton.setBackgroundColor(ContextCompat.getColor(this, R.color.purple_200))
                            }
                        }
                    }
                } else {
                    outputText.text = "Storage permission not granted!"
                }
            }
        }

        continueButton.setOnClickListener {
            val externalStorageDir: File = getExternalFilesDir(null) ?: Environment.getExternalStorageDirectory()
            val novelFolder = File(externalStorageDir, novel)
            val continueFile = File(novelFolder, "continue")
            val intent = Intent(this, chapterActivity::class.java)
            intent.putExtra("novelName", novel)

            if (continueFile.exists()) {
                try {
                    val content = continueFile.readText()
                    intent.putExtra("chapterNo", content)
                    startActivity(intent)
                } catch (e: IOException) {
                    runOnUiThread {
                        outputText.text = "Error reading the continue file: ${e.message}"
                    }
                }
            } else {
                intent.putExtra("chapterNo", "1")
                writeToContinueFile("1", novel, outputText)
            }
        }

        home.setOnClickListener {
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }


    }

    private fun hasStoragePermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            true
        } else {
            val permission = ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.WRITE_EXTERNAL_STORAGE
            )
            permission == PackageManager.PERMISSION_GRANTED
        }
    }

    @SuppressLint("SetTextI18n")
    fun writeToContinueFile(content: String, novel: String, outputText: TextView) {
        val externalStorageDir: File = getExternalFilesDir(null) ?: Environment.getExternalStorageDirectory()
        val novelFolder = File(externalStorageDir, novel)
        val continueFile = File(novelFolder, "continue")

        try {
            continueFile.writeText(content)
            runOnUiThread {
                outputText.text = "Content written to continue file."
            }
        } catch (e: IOException) {
            runOnUiThread {
                outputText.text = "Error writing to the continue file: ${e.message}"
            }
        }
    }

    private fun requestStoragePermission() {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE, Manifest.permission.READ_EXTERNAL_STORAGE),
            permsCode
        )
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == permsCode) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                // Permission granted, proceed with file operations
            } else {
                // Permission denied, inform the user
                "Storage permission is required to save files.".also { findViewById<TextView>(R.id.outputText).text = it }
            }
        }
    }
}
