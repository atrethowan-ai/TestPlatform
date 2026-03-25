package com.testplatform.quizwrapper.ui.selector

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.cardview.widget.CardView
import androidx.lifecycle.lifecycleScope
import com.testplatform.quizwrapper.R
import com.testplatform.quizwrapper.config.AppConfig
import com.testplatform.quizwrapper.config.ServerConfigRepository
import com.testplatform.quizwrapper.ui.main.MainActivity
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.net.HttpURLConnection
import java.net.URL

class ServerSelectorActivity : AppCompatActivity() {

    private lateinit var server1Card: CardView
    private lateinit var server2Card: CardView
    private lateinit var server1Status: TextView
    private lateinit var server2Status: TextView
    private lateinit var refreshButton: Button
    private lateinit var serverConfigRepository: ServerConfigRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_server_selector)

        serverConfigRepository = ServerConfigRepository(this)

        server1Card = findViewById(R.id.server1_card)
        server2Card = findViewById(R.id.server2_card)
        server1Status = findViewById(R.id.server1_status)
        server2Status = findViewById(R.id.server2_status)
        refreshButton = findViewById(R.id.refresh_button)

        server1Card.setOnClickListener { selectServer(AppConfig.serverUrl1) }
        server2Card.setOnClickListener { selectServer(AppConfig.serverUrl2) }
        refreshButton.setOnClickListener { checkServers() }

        checkServers()
    }

    private fun selectServer(url: String) {
        serverConfigRepository.saveServerUrl(url)
        val intent = Intent(this, MainActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }

    private fun checkServers() {
        server1Status.text = "Checking..."
        server1Status.setTextColor(Color.GRAY)
        server2Status.text = "Checking..."
        server2Status.setTextColor(Color.GRAY)

        checkServerStatus(AppConfig.serverUrl1, server1Status)
        checkServerStatus(AppConfig.serverUrl2, server2Status)
    }

    private fun checkServerStatus(url: String, statusText: TextView) {
        lifecycleScope.launch {
            val isUp = withContext(Dispatchers.IO) {
                try {
                    val connection = URL(url).openConnection() as HttpURLConnection
                    connection.connectTimeout = 2000
                    connection.readTimeout = 2000
                    connection.requestMethod = "HEAD"
                    val responseCode = connection.responseCode
                    responseCode in 200..399
                } catch (e: Exception) {
                    false
                }
            }

            if (isUp) {
                statusText.text = "Server is UP"
                statusText.setTextColor(Color.parseColor("#4CAF50"))
            } else {
                statusText.text = "Server is DOWN"
                statusText.setTextColor(Color.RED)
            }
        }
    }
}
