# voice_input.py
def get_voice_input_html():
    """
    Returns HTML and JavaScript code for a button that triggers speech recognition.
    The transcribed text is appended to the URL as a query parameter.
    """
    return """
    <button id="speak">Speak</button>
    <script>
    const speakButton = document.getElementById('speak');
    speakButton.addEventListener('click', () => {
        if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'en-US';  // Set language to English (US)
            recognition.start();
            recognition.onresult = (event) => {
                const transcribedText = event.results[0][0].transcript;
                window.location.href = window.location.pathname + '?transcribed=' + encodeURIComponent(transcribedText);
            };
        } else {
            alert('Speech recognition not supported in this browser.');
        }
    });
    </script>
    """
