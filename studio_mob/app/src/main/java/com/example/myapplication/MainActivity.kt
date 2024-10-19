package com.example.myapplication

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.util.Log
import android.view.Gravity
import android.widget.Button
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.bumptech.glide.Glide
import androidx.cardview.widget.CardView
import androidx.compose.material3.TextFieldColors
import java.io.File

class MainActivity : AppCompatActivity() {

    private val permsCode = 420

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val directoryLayout: LinearLayout = findViewById(R.id.directoryLayout)

        if (!hasStoragePermission()) {
            requestStoragePermission()
        } else {
            displayDirectories(directoryLayout)
        }
        val addNovelButton: Button = findViewById(R.id.addNovel)
        addNovelButton.setOnClickListener() {
            val intent = Intent(this, addNovel::class.java)
            startActivity(intent)
        }
    }

    private fun hasStoragePermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            true
        } else {
            val permission = ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.READ_EXTERNAL_STORAGE
            )
            permission == PackageManager.PERMISSION_GRANTED
        }
    }

    private fun requestStoragePermission() {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(Manifest.permission.READ_EXTERNAL_STORAGE, Manifest.permission.WRITE_EXTERNAL_STORAGE),
            permsCode
        )
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == permsCode) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                val directoryLayout: LinearLayout = findViewById(R.id.directoryLayout)
                displayDirectories(directoryLayout)
            }
        }
    }

    private fun displayDirectories(directoryLayout: LinearLayout) {
        val externalStorageDir = getExternalFilesDir(null) ?: Environment.getExternalStorageDirectory()

        if (externalStorageDir.exists() && externalStorageDir.isDirectory) {
            val subDirs = externalStorageDir.listFiles()?.filter { it.isDirectory }

            subDirs?.forEach { subDir ->
                val subDirName = subDir.name
                val imageFile = File(subDir, "image.jpg")
                val cardView = CardView(this).apply {
                    layoutParams = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT
                    ).apply {
                        setMargins(0, 70, 0, 0)
                        gravity = Gravity.CENTER_HORIZONTAL
                    }
                    radius = 40f
                    cardElevation = 4f
                    setContentPadding(16, 16, 16, 16)
                    setCardBackgroundColor(Color.parseColor("#383838"))
                    isClickable = true
                    isFocusable = true
                    foregroundGravity = Gravity.CENTER_HORIZONTAL
                }
                val novel = LinearLayout(this)
                novel.orientation = LinearLayout.VERTICAL
                novel.gravity = Gravity.CENTER_HORIZONTAL
                novel.layoutParams = LinearLayout.LayoutParams(
                    550,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                )

                if (imageFile.exists()) {
                    val imageThing = ImageView(this).apply {
                        layoutParams = LinearLayout.LayoutParams(350, 550).apply {
                            gravity = Gravity.CENTER
                        }
                        scaleType = ImageView.ScaleType.FIT_CENTER
                        setImageResource(R.drawable.ic_launcher_foreground)
                    }
                    Glide.with(this).load(imageFile).into(imageThing)

                    novel.addView(imageThing)
                }

                val textThing = TextView(this).apply {
                    layoutParams = LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT).apply {
                        gravity = Gravity.CENTER
                        topMargin = 2
                        setPadding(10, 0, 10,20)
                    }
                    text = subDirName.split('-')
                        .joinToString(" ") { word -> word.replaceFirstChar { it.uppercase() } }
                        textSize = 16f
                        setTextColor(Color.WHITE)
                        gravity = Gravity.CENTER
                    }
                novel.addView(textThing)
                cardView.addView(novel)
                directoryLayout.addView(cardView)
                cardView.setOnClickListener {
                    val intent = Intent(this, novelActivity::class.java)
                    intent.putExtra("novelName", subDir.name)
                    startActivity(intent)
                }
            }
        } else {
            Log.d("MainActivity", "Folder not found or it's not a directory!")
        }
    }
}
