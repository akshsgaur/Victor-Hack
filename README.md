# Speech-to-Code Application

A web appl

https://github.com/user-attachments/assets/1579525e-0c72-4dd9-81e0-3af179d327a1

ication that converts voice commands into functional code. Simply speak your requirements, and the application will generate and run the corresponding code in real-time.

## Installation

1. Clone the repo
2. Add a `.env` file with an `OPENAI_API_KEY`
3. Run either `python speech-to-code.py --web` or `python speech-to-code.py --cli`

## Features

- Voice command recognition
- Real-time code generation
- Live preview of generated code
- Support for multiple application types:
  - Snake Game
  - Calculator
  - Todo List
- Command history tracking
- Modern, responsive UI

## Supported Commands

The application currently supports the following voice commands:
- "Build me a Snake game"
- "Create a calculator"
- "Make a simple todo list"

## Requirements

- Modern web browser (Chrome or Edge recommended)
- Microphone access
- Internet connection
- OpenAI API key

## How to Use

1. Open the application in your web browser
2. Click the "Start Listening" button
3. Speak one of the supported commands clearly
4. Wait for the code to be generated
5. Click "Run Code" to see the application in action
6. Use "Stop" to end the preview
7. Use "Clear Results" to reset the application

## Technical Details

- Built with Python and Flask backend
- Uses OpenAI's API for code generation and enhancement
- Speech recognition (via browser or speech_recognition library)
- Multiple AI agent system:
  - Code Generator Agent - Creates initial code
  - Code Debugger Agent - Finds and fixes errors
  - Code Executor Agent - Runs and tests the code
  - Code Explainer Agent - Provides explanations
  - Code Enhancer Agent - Improves code based on feedback
- Responsive web interface

## Browser Support

The application works best in modern browsers that support the Web Speech API:
- Google Chrome (recommended)
- Microsoft Edge
- Other browsers with Web Speech API support

## Limitations

- Requires browser support for Web Speech API
- Limited to predefined application types
- Voice recognition accuracy depends on microphone quality and environment
- Requires OpenAI API key

## Future Improvements

- Support for more application types
- Custom code templates
- Code export functionality
- Enhanced error handling
- Additional styling options

## Contributing

Feel free to fork the repository and submit pull requests for any improvements.
