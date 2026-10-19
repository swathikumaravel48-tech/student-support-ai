// Global variables
const API_URL = 'http://localhost:5000';
let sessionId = generateSessionId();
let messageCount = 0;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('sessionId').textContent = sessionId.substring(0, 8) + '...';
    console.log('Student Support Assistant loaded. Session:', sessionId);
});

// Generate unique session ID
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Send message function
function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    userInput.value = '';
    
    // Show loading indicator
    showLoadingIndicator(true);
    
    // Send to backend
    fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: sessionId,
            message: message
        })
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        showLoadingIndicator(false);
        addMessageToChat(data.response, 'assistant');
        messageCount++;
        document.getElementById('messageCount').textContent = messageCount;
        
        // Auto-scroll to bottom
        scrollToBottom();
    })
    .catch(error => {
        showLoadingIndicator(false);
        console.error('Error:', error);
        addMessageToChat('Sorry, I encountered an error processing your request. Please try again.', 'assistant');
    });
}

// Add message to chat display
function addMessageToChat(message, role) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Parse markdown-like formatting
    let formattedMessage = message;
    formattedMessage = formattedMessage.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formattedMessage = formattedMessage.replace(/\n/g, '<br>');
    formattedMessage = formattedMessage.replace(/- (.*?)<br>/g, '<li>$1</li>');
    
    // Wrap lists in ul tags
    if (formattedMessage.includes('<li>')) {
        formattedMessage = '<ul>' + formattedMessage.replace(/<li>(.*?)<\/li>/g, '<li>$1</li>') + '</ul>';
    }
    
    contentDiv.innerHTML = formattedMessage;
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    scrollToBottom();
}

// Scroll to bottom of chat
function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

// Show/hide loading indicator
function showLoadingIndicator(show) {
    document.getElementById('loadingIndicator').style.display = show ? 'block' : 'none';
}

// Handle Enter key in input
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Clear chat history
function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
        messageCount = 0;
        document.getElementById('messageCount').textContent = '0';
        
        // Generate new session
        sessionId = generateSessionId();
        document.getElementById('sessionId').textContent = sessionId.substring(0, 8) + '...';
        
        // Call clear session endpoint
        fetch(`${API_URL}/api/clear-session/${sessionId}`, {
            method: 'DELETE'
        });
        
        // Add greeting message
        addMessageToChat('Chat cleared! How can I help you today?', 'assistant');
    }
}

// Search FAQs
function searchFAQ() {
    fetch(`${API_URL}/api/faq`)
        .then(response => response.json())
        .then(data => {
            let faqText = '<strong>Frequently Asked Questions:</strong>\n\n';
            data.faqs.slice(0, 5).forEach((faq, index) => {
                faqText += `${index + 1}. **${faq.question}**\n   ${faq.answer.substring(0, 100)}...\n\n`;
            });
            addMessageToChat(faqText, 'assistant');
        })
        .catch(error => {
            console.error('Error fetching FAQs:', error);
            addMessageToChat('Sorry, I could not retrieve the FAQs. Please try again.', 'assistant');
        });
}

// Search Regulations
function searchRegulations() {
    fetch(`${API_URL}/api/regulations`)
        .then(response => response.json())
        .then(data => {
            let regText = '<strong>College Regulations:</strong>\n\n';
            data.regulations.slice(0, 5).forEach((reg, index) => {
                regText += `${index + 1}. **${reg.title}**\n`;
            });
            addMessageToChat(regText, 'assistant');
        })
        .catch(error => {
            console.error('Error fetching regulations:', error);
            addMessageToChat('Sorry, I could not retrieve the regulations. Please try again.', 'assistant');
        });
}

// Search Syllabus
function searchSyllabus() {
    const subjects = ['python', 'web_development', 'database', 'cloud_computing', 'data_science'];
    let syllabusText = '<strong>Available Courses:</strong>\n\n';
    syllabusText += subjects.map((s, i) => `${i + 1}. ${s.replace(/_/g, ' ').toUpperCase()}`).join('\n');
    syllabusText += '\n\nWhich course would you like to learn about?';
    addMessageToChat(syllabusText, 'assistant');
}

// Ask about a specific topic
function askAbout(topic) {
    document.getElementById('userInput').value = topic;
    sendMessage();
    return false;
}

// Suggestions modal functions
function closeSuggestions() {
    document.getElementById('suggestionsModal').style.display = 'none';
}

// Click outside modal to close
window.onclick = function(event) {
    const modal = document.getElementById('suggestionsModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

// Error handling for API calls
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (!response.ok) {
            console.warn('API health check failed');
            addMessageToChat('⚠️ Backend connection issue. Please ensure the Flask server is running on port 5000.', 'assistant');
        }
    } catch (error) {
        console.error('Cannot connect to API:', error);
        addMessageToChat('⚠️ Cannot connect to the backend. Please start the Flask server: python app.py', 'assistant');
    }
}

// Check API on load
setTimeout(checkAPIHealth, 2000);
