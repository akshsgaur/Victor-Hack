import os
import time
import re
import sys
import subprocess
import tempfile
from pathlib import Path
import logging
import json
from typing import Dict, List, Optional, Union, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import OpenAI with new client format first
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    USE_NEW_OPENAI = True
    logger.info("Using new OpenAI client")
except ImportError:
    # Fall back to old format
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    USE_NEW_OPENAI = False
    logger.info("Using legacy OpenAI package")

# Try to import speech recognition
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
    logger.info("Speech recognition available")
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.info("Speech recognition not available")

# For web interface
from flask import Flask, request, jsonify, render_template, send_from_directory

# Path to save generated code
GENERATED_CODE_DIR = Path("generated_code")
GENERATED_CODE_DIR.mkdir(exist_ok=True)

# Initialize Flask app
app = Flask(__name__)

class CodeGeneratorAgent:
    """Agent responsible for generating code based on natural language descriptions"""
    
    def __init__(self, model="gpt-4.1-nano"):
        self.model = model
        logger.info(f"Initialized CodeGeneratorAgent with model: {model}")
    
    def generate(self, description: str) -> str:
        """Generate code based on description"""
        logger.info(f"Generating code for: {description}")
        
        # System prompt designed for high-quality code generation
        system_prompt = """You are an expert Python programming agent specialized in generating production-quality code. 
Your code should be:
1. Well-structured and organized
2. Thoroughly commented
3. Error-handled with try/except blocks
4. Using best practices and design patterns
5. Complete and ready to run without missing dependencies
6. Include self-checks to verify if required libraries are installed

If you generate code that requires external libraries, include code to check if they're installed and provide 
instructions on how to install them if they're not."""
        
        user_prompt = f"""Generate Python code for: {description}
        
Make sure the code is complete, executable, and robust. Include proper error handling and all necessary imports.
If the code requires external libraries, add code that checks if they're installed and provides instructions to install them.

Return ONLY the full Python code with no additional explanations."""
        
        try:
            if USE_NEW_OPENAI:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=4000
                )
                code = response.choices[0].message.content
            else:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=4000
                )
                code = response.choices[0].message.content
            
            # Extract code from potential markdown format
            if "```python" in code and "```" in code.split("```python", 1)[1]:
                code = code.split("```python", 1)[1].split("```", 1)[0].strip()
            elif "```" in code:
                code = code.split("```", 1)[1].split("```", 1)[0].strip()
            
            logger.info(f"Successfully generated code ({len(code)} characters)")
            return code
        
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            return f"# Error generating code: {str(e)}"


class CodeDebuggerAgent:
    """Agent responsible for debugging and fixing code"""
    
    def __init__(self, model="gpt-4.1-nano"):
        self.model = model
        logger.info(f"Initialized CodeDebuggerAgent with model: {model}")
    
    def debug(self, code: str, error_message: str = None) -> str:
        """Debug code by fixing potential errors"""
        if error_message:
            logger.info(f"Debugging code with error: {error_message[:100]}...")
        else:
            logger.info("Doing preventive debugging of code")
        
        # System prompt designed for debugging
        system_prompt = """You are an expert Python debugging agent specialized in finding and fixing errors in code.
Focus on:
1. Syntax errors
2. Runtime errors
3. Logical errors
4. Missing dependencies
5. Environment compatibility issues

Fix the code comprehensively. Don't just address the immediate error; look for other potential issues 
that might arise after the first one is fixed."""
        
        if error_message:
            user_prompt = f"""Debug this Python code that has the following error:
ERROR:
{error_message}

CODE:
```python
{code}
```

Return ONLY the complete fixed code with no explanations."""
        else:
            user_prompt = f"""Analyze this Python code for potential errors or improvements:
```python
{code}
```

Return ONLY the complete improved code with no explanations."""
        
        try:
            if USE_NEW_OPENAI:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=4000
                )
                fixed_code = response.choices[0].message.content
            else:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=4000
                )
                fixed_code = response.choices[0].message.content
            
            # Extract code from potential markdown format
            if "```python" in fixed_code and "```" in fixed_code.split("```python", 1)[1]:
                fixed_code = fixed_code.split("```python", 1)[1].split("```", 1)[0].strip()
            elif "```" in fixed_code:
                fixed_code = fixed_code.split("```", 1)[1].split("```", 1)[0].strip()
            
            logger.info("Successfully debugged code")
            return fixed_code
        
        except Exception as e:
            logger.error(f"Error debugging code: {str(e)}")
            return code  # Return original code if debugging fails


class CodeExecutorAgent:
    """Agent responsible for running code and handling dependencies"""
    
    def __init__(self):
        logger.info("Initialized CodeExecutorAgent")
        self.installed_packages = self._get_installed_packages()
    
    def _get_installed_packages(self) -> List[str]:
        """Get a list of already installed packages"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                return [pkg["name"].lower() for pkg in packages]
            return []
        except Exception as e:
            logger.error(f"Error getting installed packages: {e}")
            return []
    
    def extract_required_packages(self, code: str) -> List[str]:
        """Extract required packages from code"""
        # Simple regex pattern to find import statements
        import_pattern = re.compile(r'(?:from|import)\s+([a-zA-Z0-9_]+)')
        matches = import_pattern.findall(code)
        
        # Common Python standard libraries that don't need installation
        std_libs = {
            'os', 'sys', 'time', 're', 'math', 'random', 'datetime', 'json',
            'collections', 'itertools', 'functools', 'operator', 'string',
            'pathlib', 'typing', 'enum', 'copy', 'pickle', 'csv', 'argparse',
            'threading', 'multiprocessing', 'queue', 'logging', 'io', 'tempfile',
            'traceback', 'unittest', 'sqlite3', 'xml', 'html', 'urllib', 'http',
            'base64', 'hashlib', 'ssl', 'socket', 'email', 'calendar'
        }
        
        # Filter out standard libraries
        packages = [match for match in matches if match not in std_libs]
        
        # Map package names to PyPI names where they differ
        package_mapping = {
            'pygame': 'pygame',
            'numpy': 'numpy',
            'np': 'numpy',
            'pd': 'pandas',
            'pandas': 'pandas',
            'sklearn': 'scikit-learn',
            'matplotlib': 'matplotlib',
            'plt': 'matplotlib',
            'bs4': 'beautifulsoup4',
            'PIL': 'pillow',
            'cv2': 'opencv-python',
            'tk': 'tk',
            'tkinter': 'tk',
            'requests': 'requests',
            'flask': 'flask',
            'django': 'django',
            'tf': 'tensorflow',
            'tensorflow': 'tensorflow',
            'torch': 'torch',
            'seaborn': 'seaborn',
            'sns': 'seaborn'
        }
        
        # Return list of required packages with proper PyPI names
        required = []
        for pkg in packages:
            if pkg in package_mapping:
                pkg_name = package_mapping[pkg]
                if pkg_name.lower() not in [p.lower() for p in required]:
                    required.append(pkg_name)
        
        logger.info(f"Extracted required packages: {required}")
        return required
    
    def is_package_installed(self, package_name: str) -> bool:
        """Check if a package is already installed"""
        return package_name.lower() in [p.lower() for p in self.installed_packages]
    
    def install_required_packages(self, packages: List[str]) -> str:
        """Install required packages using pip"""
        if not packages:
            return ""
        
        output = "Checking required packages:\n"
        packages_to_install = []
        
        # First identify which packages need installation
        for package in packages:
            if self.is_package_installed(package):
                output += f"✓ {package} is already installed\n"
            else:
                output += f"⟳ {package} needs to be installed\n"
                packages_to_install.append(package)
        
        # Then install packages that need installation
        for package in packages_to_install:
            try:
                output += f"Installing {package}...\n"
                
                # First try normal installation (no --user flag)
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", package],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    if result.returncode == 0:
                        output += f"✓ Successfully installed {package}\n"
                        # Add to installed packages list
                        self.installed_packages.append(package.lower())
                    else:
                        output += f"✗ Failed to install {package}: {result.stderr}\n"
                        # Try alternative installation methods if standard method fails
                        if "No matching distribution" in result.stderr:
                            output += f"Trying alternative package name for {package}...\n"
                            # Some packages have different names than their import names
                            alt_names = {
                                'PIL': 'pillow',
                                'cv2': 'opencv-python',
                                'sklearn': 'scikit-learn'
                            }
                            if package in alt_names:
                                alt_package = alt_names[package]
                                alt_result = subprocess.run(
                                    [sys.executable, "-m", "pip", "install", alt_package],
                                    capture_output=True,
                                    text=True,
                                    timeout=120
                                )
                                if alt_result.returncode == 0:
                                    output += f"✓ Successfully installed {alt_package} (alternative for {package})\n"
                                    self.installed_packages.append(alt_package.lower())
                                else:
                                    output += f"✗ Failed to install alternative package: {alt_result.stderr}\n"
                        
                except subprocess.TimeoutExpired:
                    output += f"✗ Installation timed out for {package}\n"
                
            except Exception as e:
                output += f"✗ Error installing {package}: {str(e)}\n"
        
        # Update installed packages list after installations
        self.installed_packages = self._get_installed_packages()
        return output
    
    def execute(self, code: str, timeout: int = 6000) -> Tuple[bool, str]:
        """Execute code and return result"""
        logger.info("Executing code")
        
        # First, extract and install required packages
        required_packages = self.extract_required_packages(code)
        installation_output = self.install_required_packages(required_packages)
        
        # Check if code contains any GUI elements (Pygame, tkinter, etc.)
        # as those might cause issues in headless environments
        has_gui = any(pkg in ' '.join(required_packages).lower() for pkg in ['pygame', 'tk', 'matplotlib'])
        
        # Add a warning for GUI applications
        if has_gui:
            installation_output += "\nNote: This code contains GUI elements and may require a display to run properly.\n\n"
        
        # Save code to temporary file
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code.encode('utf-8'))
        
        try:
            # Run code in subprocess
            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            os.unlink(temp_file_path)  # Clean up temp file
            
            if result.returncode == 0:
                output = installation_output + "\n" + result.stdout if installation_output else result.stdout
                logger.info("Code executed successfully")
                return True, output
            else:
                error = installation_output + "\n" + result.stderr if installation_output else result.stderr
                logger.error(f"Code execution failed: {error}")
                return False, error
        
        except subprocess.TimeoutExpired:
            os.unlink(temp_file_path)  # Clean up temp file
            logger.error(f"Code execution timed out after {timeout} seconds")
            return False, f"Execution timed out after {timeout} seconds"
        
        except Exception as e:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)  # Clean up temp file
            logger.error(f"Error during code execution: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def execute(self, code: str, timeout: int = 30) -> Tuple[bool, str]:
        """Execute code and return result"""
        logger.info("Executing code")
        
        # First, extract and install required packages
        required_packages = self.extract_required_packages(code)
        installation_output = self.install_required_packages(required_packages)
        
        # Save code to temporary file
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code.encode('utf-8'))
        
        try:
            # Run code in subprocess
            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            os.unlink(temp_file_path)  # Clean up temp file
            
            if result.returncode == 0:
                output = installation_output + "\n" + result.stdout if installation_output else result.stdout
                logger.info("Code executed successfully")
                return True, output
            else:
                error = installation_output + "\n" + result.stderr if installation_output else result.stderr
                logger.error(f"Code execution failed: {error}")
                return False, error
        
        except subprocess.TimeoutExpired:
            os.unlink(temp_file_path)  # Clean up temp file
            logger.error(f"Code execution timed out after {timeout} seconds")
            return False, f"Execution timed out after {timeout} seconds"
        
        except Exception as e:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)  # Clean up temp file
            logger.error(f"Error during code execution: {str(e)}")
            return False, f"Error: {str(e)}"


class CodeExplainerAgent:
    """Agent responsible for explaining code"""
    
    def __init__(self, model="gpt-4-turbo-preview"):
        self.model = model
        logger.info(f"Initialized CodeExplainerAgent with model: {model}")
    
    def explain(self, code: str) -> str:
        """Provide a clear explanation of how the code works"""
        logger.info("Generating code explanation")
        
        system_prompt = """You are an expert Python education agent specialized in explaining code clearly.
You break down complex concepts into simple explanations that even beginners can understand.
Focus on explaining:
1. The overall purpose of the code
2. How the different parts work together
3. Key programming concepts used
4. The flow of execution
5. How to use and modify the code"""
        
        user_prompt = f"""Explain how this Python code works:
```python
{code}
```

Provide a clear, concise explanation with a focus on helping someone understand the code fully."""
        
        try:
            if USE_NEW_OPENAI:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                explanation = response.choices[0].message.content
            else:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                explanation = response.choices[0].message.content
            
            logger.info("Successfully generated code explanation")
            return explanation
        
        except Exception as e:
            logger.error(f"Error explaining code: {str(e)}")
            return f"Error generating explanation: {str(e)}"


class CodeEnhancerAgent:
    """Agent responsible for enhancing code based on user feedback"""
    
    def __init__(self, model="gpt-4.1-nano"):
        self.model = model
        logger.info(f"Initialized CodeEnhancerAgent with model: {model}")
    
    def enhance(self, code: str, feedback: str) -> str:
        """Enhance code based on user feedback"""
        logger.info(f"Enhancing code with feedback: {feedback[:100]}...")
        
        system_prompt = """You are an expert Python enhancement agent specialized in improving code based on user feedback.
Focus on:
1. Implementing the requested changes accurately
2. Maintaining code quality and readability
3. Adding proper documentation for new features
4. Ensuring backward compatibility
5. Optimizing performance where possible"""
        
        user_prompt = f"""Enhance this Python code based on the following feedback:
FEEDBACK:
{feedback}

CODE:
```python
{code}
```

Return ONLY the complete enhanced code with no explanations."""
        
        try:
            if USE_NEW_OPENAI:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=4000
                )
                enhanced_code = response.choices[0].message.content
            else:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=4000
                )
                enhanced_code = response.choices[0].message.content
            
            # Extract code from potential markdown format
            if "```python" in enhanced_code and "```" in enhanced_code.split("```python", 1)[1]:
                enhanced_code = enhanced_code.split("```python", 1)[1].split("```", 1)[0].strip()
            elif "```" in enhanced_code:
                enhanced_code = enhanced_code.split("```", 1)[1].split("```", 1)[0].strip()
            
            logger.info("Successfully enhanced code")
            return enhanced_code
        
        except Exception as e:
            logger.error(f"Error enhancing code: {str(e)}")
            return code  # Return original code if enhancement fails


class SpeechToCodeOrchestrator:
    """Orchestrator that coordinates the different agents"""
    
    def __init__(self):
        self.generator = CodeGeneratorAgent()
        self.debugger = CodeDebuggerAgent()
        self.executor = CodeExecutorAgent()
        self.explainer = CodeExplainerAgent()
        self.enhancer = CodeEnhancerAgent()
        logger.info("Initialized SpeechToCodeOrchestrator")
    
    def process_request(self, text_request: str) -> Dict:
        """Process a text request through the agent pipeline"""
        logger.info(f"Processing request: {text_request}")
        
        # Step 1: Generate initial code
        generated_code = self.generator.generate(text_request)
        
        # Step 2: Preventive debugging (without specific error)
        debugged_code = self.debugger.debug(generated_code)
        
        # Step 3: Try to execute the code
        success, output = self.executor.execute(debugged_code)
        
        # Step 4: If execution failed, debug with the specific error
        if not success:
            logger.info("Initial execution failed, attempting to fix...")
            fixed_code = self.debugger.debug(debugged_code, output)
            
            # Try execution again
            success, output = self.executor.execute(fixed_code)
            if success:
                debugged_code = fixed_code
            else:
                # One more attempt with a different approach
                logger.info("Second execution failed, final debugging attempt...")
                final_code = self.debugger.debug(fixed_code, output)
                success, output = self.executor.execute(final_code)
                if success:
                    debugged_code = final_code
        
        # Step 5: Generate explanation
        explanation = self.explainer.explain(debugged_code)
        
        # Generate a unique filename and save the code
        timestamp = int(time.time())
        filename = f"code_{timestamp}.py"
        filepath = GENERATED_CODE_DIR / filename
        
        with open(filepath, 'w') as f:
            f.write(debugged_code)
        
        return {
            "success": success,
            "code": debugged_code,
            "output": output,
            "explanation": explanation,
            "filename": filename
        }
    
    def enhance_code(self, code: str, feedback: str) -> Dict:
        """Enhance existing code based on user feedback"""
        logger.info(f"Enhancing code with feedback: {feedback[:100]}...")
        
        enhanced_code = self.enhancer.enhance(code, feedback)
        
        # Debug the enhanced code
        debugged_code = self.debugger.debug(enhanced_code)
        
        # Try to execute
        success, output = self.executor.execute(debugged_code)
        
        # If execution failed, debug with the specific error
        if not success:
            logger.info("Enhanced code execution failed, attempting to fix...")
            fixed_code = self.debugger.debug(debugged_code, output)
            
            # Try execution again
            success, output = self.executor.execute(fixed_code)
            if success:
                debugged_code = fixed_code
        
        # Generate explanation of changes
        explanation = self.explainer.explain(debugged_code)
        
        # Generate a unique filename and save the code
        timestamp = int(time.time())
        filename = f"enhanced_{timestamp}.py"
        filepath = GENERATED_CODE_DIR / filename
        
        with open(filepath, 'w') as f:
            f.write(debugged_code)
        
        return {
            "success": success,
            "code": debugged_code,
            "output": output,
            "explanation": explanation,
            "filename": filename
        }
    
    def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio to text using speech recognition"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            logger.error("Speech recognition not available")
            return None
        
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_file_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                logger.info(f"Transcribed text: {text}")
                return text
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return None


# Flask routes for web interface
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process-text', methods=['POST'])
def process_text_api():
    """Process a text request and generate code"""
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    text = data['text']
    
    try:
        orchestrator = SpeechToCodeOrchestrator()
        result = orchestrator.process_request(text)
        
        return jsonify(result)
    except Exception as e:
        logger.exception("Error processing request")
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhance-code', methods=['POST'])
def enhance_code_api():
    """Enhance existing code based on feedback"""
    data = request.json
    if not data or 'code' not in data or 'feedback' not in data:
        return jsonify({'error': 'Both code and feedback must be provided'}), 400
    
    code = data['code']
    feedback = data['feedback']
    
    try:
        orchestrator = SpeechToCodeOrchestrator()
        result = orchestrator.enhance_code(code, feedback)
        
        return jsonify(result)
    except Exception as e:
        logger.exception("Error enhancing code")
        return jsonify({'error': str(e)}), 500



# @app.route('/api/transcribe', methods=['POST'])
# def transcribe_api():
#     """Transcribe audio to text using OpenAI Whisper API"""
#     if 'audio' not in request.files:
#         return jsonify({'success': False, 'error': 'No audio file provided'}), 400

#     audio_file = request.files['audio']

#     # Save audio temporarily
#     temp_audio_path = tempfile.mktemp(suffix=".webm")
#     audio_file.save(temp_audio_path)

#     try:
#         with open(temp_audio_path, "rb") as audio:
#             transcription = client.audio.transcriptions.create(
#                 file=audio,
#                 model="whisper-1",
#                 response_format="text"
#             )

#         # Clean up
#         os.remove(temp_audio_path)

#         logger.info(f"Transcription successful: {transcription}")
#         return jsonify({'success': True, 'text': transcription})

#     except Exception as e:
#         if os.path.exists(temp_audio_path):
#             os.remove(temp_audio_path)
#         logger.exception("Error during transcription")
#         return jsonify({'success': False, 'error': str(e)}), 500




@app.route('/api/transcribe', methods=['POST'])
def transcribe_api():
    """Transcribe audio to text using OpenAI Whisper API"""
    if 'audio' not in request.files:
        logger.error("No audio file provided in request")
        return jsonify({'success': False, 'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    logger.info(f"Received audio file: {audio_file.filename}, Content type: {audio_file.content_type}")

    # Save audio temporarily with appropriate extension based on content type
    content_type = audio_file.content_type
    extension = ".wav"  # Default extension
    
    if "webm" in content_type:
        extension = ".webm"
    elif "mp3" in content_type:
        extension = ".mp3"
    elif "ogg" in content_type:
        extension = ".ogg"
    
    temp_audio_path = tempfile.mktemp(suffix=extension)
    logger.info(f"Saving audio to temporary file: {temp_audio_path}")
    
    try:
        audio_file.save(temp_audio_path)
        logger.info(f"Audio file saved, size: {os.path.getsize(temp_audio_path)} bytes")
        
        # First try to use OpenAI Whisper API if available
        if USE_NEW_OPENAI:
            try:
                logger.info("Attempting transcription with OpenAI Whisper API")
                with open(temp_audio_path, "rb") as audio:
                    transcription = client.audio.transcriptions.create(
                        file=audio,
                        model="whisper-1"
                    )
                
                text = transcription.text
                logger.info(f"OpenAI Whisper transcription successful: {text}")
                
                # Clean up
                os.remove(temp_audio_path)
                return jsonify({'success': True, 'text': text})
            
            except Exception as e:
                logger.error(f"OpenAI Whisper transcription failed: {str(e)}")
                # Fall through to try other methods
        
        # If OpenAI transcription failed or not available, try speech_recognition
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                logger.info("Attempting transcription with speech_recognition")
                recognizer = sr.Recognizer()
                
                # Handle different audio formats
                if extension == ".webm":
                    # Convert webm to wav using ffmpeg if available
                    try:
                        wav_path = tempfile.mktemp(suffix=".wav")
                        subprocess.run(
                            ["ffmpeg", "-i", temp_audio_path, wav_path],
                            check=True,
                            capture_output=True
                        )
                        temp_audio_path = wav_path
                        logger.info(f"Converted webm to wav: {wav_path}")
                    except Exception as conv_error:
                        logger.error(f"Error converting webm to wav: {str(conv_error)}")
                        # Continue with original file if conversion fails
                
                with sr.AudioFile(temp_audio_path) as source:
                    audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data)
                    logger.info(f"Speech recognition transcription successful: {text}")
                    
                    # Clean up
                    os.remove(temp_audio_path)
                    return jsonify({'success': True, 'text': text})
            
            except Exception as sr_error:
                logger.error(f"Speech recognition transcription failed: {str(sr_error)}")
                # Fall through to return error
        
        # If we got here, both methods failed
        logger.error("All transcription methods failed")
        return jsonify({
            'success': False, 
            'error': 'Transcription failed. Speech recognition is not properly configured.'
        }), 500
    
    except Exception as e:
        logger.exception("Error processing audio file")
        
        # Clean up temporary file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/execute-code', methods=['POST'])
def execute_code_api():
    """Execute code and return the result"""
    data = request.json
    if not data or 'code' not in data:
        return jsonify({'error': 'No code provided'}), 400
    
    code = data['code']
    
    try:
        executor = CodeExecutorAgent()
        success, output = executor.execute(code)
        
        return jsonify({
            'success': success,
            'output': output
        })
    except Exception as e:
        logger.exception("Error executing code")
        return jsonify({'error': str(e)}), 500

@app.route('/api/explain-code', methods=['POST'])
def explain_code_api():
    """Explain code and return the explanation"""
    data = request.json
    if not data or 'code' not in data:
        return jsonify({'error': 'No code provided'}), 400
    
    code = data['code']
    
    try:
        explainer = CodeExplainerAgent()
        explanation = explainer.explain(code)
        
        return jsonify({
            'success': True,
            'explanation': explanation
        })
    except Exception as e:
        logger.exception("Error explaining code")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download the generated code file"""
    return send_from_directory(GENERATED_CODE_DIR, filename, as_attachment=True)

# Command-line interface for testing
def cli_interface():
    """Simple command-line interface for testing the orchestrator"""
    print("=" * 50)
    print("Speech-to-Code Agentic System")
    print("=" * 50)
    print("Enter a description of the code you want to generate.")
    print("Type 'exit' to quit.")
    print()
    
    orchestrator = SpeechToCodeOrchestrator()
    
    while True:
        text = input("Request: ")
        if text.lower() == 'exit':
            break
        
        print("Processing...")
        result = orchestrator.process_request(text)
        
        print("\n" + "=" * 50)
        print("GENERATED CODE:")
        print("=" * 50)
        print(result["code"])
        
        print("\n" + "=" * 50)
        print("EXECUTION OUTPUT:")
        print("=" * 50)
        print(result["output"])
        
        print("\n" + "=" * 50)
        print("EXPLANATION:")
        print("=" * 50)
        print(result["explanation"])
        
        print("\n" + "=" * 50)
        print(f"Code saved to: {GENERATED_CODE_DIR / result['filename']}")
        print("=" * 50)
        
        enhance = input("\nWould you like to enhance this code? (y/n): ")
        if enhance.lower() == 'y':
            feedback = input("Enter your feedback for enhancement: ")
            print("Enhancing...")
            enhanced = orchestrator.enhance_code(result["code"], feedback)
            
            print("\n" + "=" * 50)
            print("ENHANCED CODE:")
            print("=" * 50)
            print(enhanced["code"])
            
            print("\n" + "=" * 50)
            print("EXECUTION OUTPUT:")
            print("=" * 50)
            print(enhanced["output"])
            
            print("\n" + "=" * 50)
            print(f"Enhanced code saved to: {GENERATED_CODE_DIR / enhanced['filename']}")
            print("=" * 50)
        
        print("\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Speech-to-Code Agentic System")
    parser.add_argument('--web', action='store_true', help='Start web interface')
    parser.add_argument('--cli', action='store_true', help='Start CLI interface')
    args = parser.parse_args()
    
    if args.web:
        print("Starting web interface on https://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=3010, ssl_context=("./cert.pem", "./key.pem")) # Changed to 0.0.0.0
    elif args.cli:
        cli_interface()
    else:
        # Default to CLI if no args provided
        cli_interface()