package com.webcraft.trademindai.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.webcraft.trademindai.data.remote.ApiService
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ChatViewModel @Inject constructor(
    private val apiService: ApiService
) : ViewModel() {

    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages

    fun sendMessage(query: String) {
        val userMsg = ChatMessage(query, true)
        _messages.value = _messages.value + userMsg
        
        viewModelScope.launch {
            try {
                val response = apiService.aiChat(query)
                val aiMsg = ChatMessage(response.response, false)
                _messages.value = _messages.value + aiMsg
            } catch (e: Exception) {
                _messages.value = _messages.value + ChatMessage("Error: ${e.message}", false)
            }
        }
    }
}

data class ChatMessage(val text: String, val isUser: Boolean)
