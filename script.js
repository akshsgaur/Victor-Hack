// Modified speech recognition code to fix the "Processing Audio..." issue

// Replace the problematic function with this improved version
function setupMediaRecorder() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.error('getUserMedia is not supported in this browser or context');
        updateStatus('Browser does not support audio recording', 'error');
        fallbackToWebSpeech();
        return;
    }

    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            try {
                console.log('[Audio] Stream acquired, setting up MediaRecorder');
                mediaRecorder = new MediaRecorder(stream);
                
                mediaRecorder.onstart = () => {
                    console.log('[Audio] Recording started');
                    audioChunks = [];
                };
                
                mediaRecorder.ondataavailable = (event) => {
                    console.log('[Audio] Data available', event.data.size);
                    audioChunks.push(event.data);
                };
                
                mediaRecorder.onstop = () => {
                    console.log('[Audio] Recording stopped, processing', audioChunks.length, 'chunks');
                    
                    if (audioChunks.length === 0) {
                        console.error('[Audio] No audio data recorded');
                        updateStatus('No audio data recorded', 'error');
                        return;
                    }
                    
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    console.log('[Audio] Created blob of size', audioBlob.size);
                    
                    // Debug: Create an audio element to test the recording
                    // const audioUrl = URL.createObjectURL(audioBlob);
                    // const audio = new Audio(audioUrl);
                    // audio.play();
                    
                    sendAudioToServer(audioBlob);
                };
                
                console.log('[Audio] MediaRecorder setup complete');
            } catch (error) {
                console.error('[Audio] MediaRecorder error:', error);
                fallbackToWebSpeech();
            }
        })
        .catch(error => {
            console.error('[Audio] Error accessing microphone:', error);
            updateStatus('Microphone access denied', 'error');
            fallbackToWebSpeech();
        });
}

// Improved send audio function with better error handling
function sendAudioToServer(audioBlob) {
    if (!audioBlob || audioBlob.size === 0) {
        console.error('[Audio] Invalid audio blob');
        updateStatus('Error: No audio data to send', 'error');
        return;
    }

    console.log('[Audio] Sending blob to server, size:', audioBlob.size);
    updateStatus('Sending audio to server...', 'processing');
    
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    
    // Log the formData for debugging
    console.log('[Audio] FormData created with audio blob');
    
    fetch('/api/transcribe', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log('[Audio] Server response status:', response.status);
        if (!response.ok) {
            throw new Error('Server returned status ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log('[Audio] Transcription response:', data);
        if (data.success && data.text) {
            transcript.value = data.text;
            processTextRequest(data.text);
        } else {
            updateStatus('Error: ' + (data.error || 'Could not transcribe audio'), 'error');
        }
    })
    .catch(error => {
        console.error('[Audio] Error sending audio:', error);
        updateStatus('Error processing audio: ' + error.message, 'error');
        
        // Automatically fall back to Web Speech API
        if (!document.querySelector('.web-speech-fallback-message')) {
            const fallbackMsg = document.createElement('div');
            fallbackMsg.className = 'web-speech-fallback-message alert alert-warning';
            fallbackMsg.innerHTML = 'Server transcription failed. Try using the text input or click the microphone again to use browser speech recognition.';
            document.querySelector('.mic-container').insertAdjacentElement('afterend', fallbackMsg);
            
            // Remove the message after 10 seconds
            setTimeout(() => {
                fallbackMsg.remove();
            }, 10000);
            
            // Try fallback method
            fallbackToWebSpeech();
        }
    });
}

// Improved Web Speech API fallback
function setupWebSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        console.warn('[Speech] Web Speech API not supported.');
        updateStatus('Speech recognition not available in this browser', 'error');
        return false;
    }

    console.log('[Speech] Setting up Web Speech API');
    
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        isRecording = true;
        micBtn.classList.add('recording');
        updateStatus('Listening with browser recognition...', 'listening');
        console.log('[Speech] Started');
    };

    recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }
        
        // Show interim results
        if (interimTranscript) {
            document.getElementById('transcript').value = finalTranscript + ' [' + interimTranscript + ']';
        }
        
        // Final results
        if (finalTranscript) {
            document.getElementById('transcript').value = finalTranscript;
        }
        
        console.log('[Speech] Transcript:', finalTranscript || interimTranscript);
    };

    recognition.onend = () => {
        isRecording = false;
        micBtn.classList.remove('recording');
        updateStatus('Processing...', 'processing');
        console.log('[Speech] Ended');

        const recognizedText = document.getElementById('transcript').value.trim();
        if (recognizedText) {
            processTextRequest(recognizedText);
        } else {
            updateStatus('No speech detected', 'error');
        }
    };

    recognition.onerror = (event) => {
        isRecording = false;
        micBtn.classList.remove('recording');
        console.error('[Speech] Error:', event.error);
        updateStatus('Speech recognition error: ' + event.error, 'error');
    };

    // Override the toggleRecording function
    window.toggleRecording = function() {
        if (isRecording) {
            recognition.stop();
        } else {
            document.getElementById('transcript').value = '';
            recognition.start();
        }
    };
    
    // Update the mic button click handler
    micBtn.onclick = window.toggleRecording;

    console.log('[Speech] Web Speech API setup complete');
    return true;
}

// Try Web Speech API directly instead of waiting for MediaRecorder to fail
function initSpeechRecognition() {
    // Check browser support and prefer Web Speech API if available
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
        console.log('[Speech] Web Speech API is available, using it as primary method');
        return setupWebSpeechRecognition();
    } 
    else if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        console.log('[Audio] Using MediaRecorder API');
        setupMediaRecorder();
        return true;
    } 
    else {
        console.error('Neither Web Speech API nor MediaRecorder are supported');
        updateStatus('Speech recognition not available in this browser', 'error');
        return false;
    }
}

// Call this to initialize speech recognition
function initializeApp() {
    // Set up the rest of the app
    setupEventListeners();
    setupTabNavigation();
    
    // Initialize speech recognition directly
    const speechInitialized = initSpeechRecognition();
    
    if (!speechInitialized) {
        // Disable mic button if speech recognition isn't available
        micBtn.disabled = true;
        micBtn.style.backgroundColor = '#ccc';
        micBtn.style.cursor = 'not-allowed';
        micBtn.title = 'Speech recognition not supported in this browser';
    }
    
    console.log('[App] Initialization complete');
}

// Replace the init function
window.addEventListener('DOMContentLoaded', initializeApp);