# 🧊 Code Compiler

**Download and Compile a Full Codebase Dump Report for any GitHub repo or folder.**

This script will compile a codebase and generate a report in markdown including each file. It will also count the number of tokens in the codebase. The output is in markdown format and perfectly formatted to be dropped into your favorite long context LLM for analysis.

It's a great way to explore and understand a codebase and has inadvertenly become a great way tool to archive our own codebase, and other open source projects not on github. It's also a great way to understand the complexity of a codebase and to identify potential security risks.

More planned features coming soon! Feel free to contribute to the project or contact us to work with us!

David Tapang / david@crewbrain.ai / CREWBRAIN.AI

## Features

### 1. Comprehensive Codebase Analysis

- Scans and analyzes entire codebases, including local directories and remote GitHub repositories.
- Supports multiple file types including Python (.py), TypeScript (.ts), JavaScript (.js), Markdown (.md), and plain text (.txt).
- Configurable file type support allows easy addition or removal of supported languages.

### 2. Detailed File Analysis

- Counts lines and characters for each file.
- Calculates token count for each file using the tiktoken library, compatible with OpenAI's tokenization.
- Provides a comprehensive overview of the codebase structure and complexity.

### 3. Flexible Report Generation

- Generates detailed reports in Markdown format, perfect for integration with LLMs or documentation systems.
- Customizable report types allow focusing on specific file types or combinations.
- Includes a directory structure overview in the report for easy navigation of the codebase.

### 4. GitHub Repository Integration

- Directly clone or update GitHub repositories for analysis.
- Handles both public and private repositories (with proper authentication).
- Displays download progress with a rich, interactive console interface.

### 5. Configurable Settings

- Customizable include/exclude folders for targeted analysis.
- Adjustable maximum file size limit to handle large codebases efficiently.
- Configurable maximum token count per file to manage analysis scope.

### 6. Intelligent File Handling

- Attempts multiple encodings (utf-8, latin-1, ascii) to read files, enhancing compatibility.
- Skips files exceeding size or token limits to prevent analysis bottlenecks.

### 7. Rich Console Interface

- Utilizes the `rich` library for a colorful, interactive console experience.
- Provides progress bars and spinners for long-running operations like file analysis and report generation.

### 8. Extensive Logging

- Comprehensive logging system captures info, warnings, and errors.
- Logs are saved to a specified file for easy troubleshooting and auditing.

### 9. Flask API Integration

- Includes a built-in Flask server to expose analysis functionality via API.
- Allows for remote triggering of codebase analysis and report generation.

### 10. Automatic Dependency Management

- Checks for required packages and attempts to install them if missing.
- Ensures all necessary dependencies are available before running the analysis.

### 11. README Extraction

- Automatically extracts and includes the content of README.md files in the generated report.
- Provides immediate context and project overview at the beginning of each report.

### 12. Token Analysis

- Calculates and reports total token count for the entire codebase.
- Useful for estimating LLM processing costs or complexity metrics.

### 13. File Type Statistics

- Generates statistics on the number of files for each supported file type.
- Offers a quick overview of the codebase composition.

### 14. Customizable Report Types

- Allows creation, modification, and deletion of report types through the settings menu.
- Enables tailored analysis for different project needs or language focuses.

### 15. Persistent Configuration

- Saves user-defined settings to a YAML configuration file.
- Allows for consistent analysis parameters across multiple runs.

### 16. Error Handling and Graceful Degradation

- Robust error handling for file reading, Git operations, and API requests.
- Continues analysis even if individual files or operations fail, ensuring maximum data collection.

### 17. Interactive Settings Management

- Provides an interactive menu for adjusting all configurable options.
- Allows real-time customization of the analysis process without editing configuration files directly.

### 18. Efficient Large Codebase Handling

- Implements generator-based file scanning to efficiently handle large directory structures.
- Manages memory usage effectively even for extensive codebases.

### 19. Secure Local Storage

- Stores downloaded repositories and generated reports in configurable local directories.
- Ensures data privacy and allows for offline analysis of previously downloaded codebases.

### 20. Extensible Architecture

- Designed with modularity in mind, allowing easy addition of new analysis types or report formats.
- Structured to facilitate future enhancements and integrations with other tools or services.

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/your-username/crewbrain-code-compiler.git
   cd crewbrain-code-compiler
   ```
2. Install Git on your system:

   * For Windows: Download and install from https://git-scm.com/download/win
   * For macOS: Use Homebrew with brew install git or download from https://git-scm.com/download/mac
   * For Linux: Use your distribution's package manager, e.g., sudo apt-get install git for Ubuntu/Debian
3. Install Requirements:

   * pip install -r requirements.txt

## Usage

The CREWBRAIN Code Compiler offers multiple ways to analyze and report on codebases:

### 1. Command-Line Interface

1. Run the script:

   ```
   python Code_Compiler.py
   ```
2. You'll be presented with a menu:

   - Choose a report type (e.g., "All Supported File Types" or "Python, TypeScript, JavaScript")
   - Access settings
   - Start the API server
   - Exit the program
3. If you choose a report type:

   - Enter the path to a local directory or a GitHub repository URL
   - The script will analyze the codebase and generate a report

### 2. API Server

1. Start the API server from the main menu or run:

   ```
   flask run
   ```
2. Send a POST request to `http://localhost:5000/api/analyze` with JSON payload:

   ```json
   {
     "source": "/path/to/local/directory or https://github.com/user/repo",
     "report_type": 1
   }
   ```
3. The server will respond with a success message or error details

### 3. Customization

Access the settings menu to customize:

- Supported file types
- Included/excluded folders
- Maximum file size and token count
- Report types
- Output directories

### 4. Output

- Reports are saved in the configured results directory (default: `output/`)
- Each report is a Markdown file named `{directory_name}_report_{report_type}.md`
- Reports include:
  - README content (if available)
  - Codebase overview (total tokens, file type counts)
  - Directory structure
  - Detailed file contents

### 5. GitHub Integration

- Directly analyze GitHub repositories by providing the URL
- The script will clone or update the repository before analysis

### 6. Logging

- Logs are saved in the `logs/` directory for debugging and auditing

### Tips

- For large codebases, consider using more specific report types or adjusting the max file size/token count, the code will automatically chunk and separate the files.
- Regularly check for updates to ensure you have the latest features and optimizations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

We appreciate your interest in Code Compiler! Here are several ways you can support the project and get assistance:

### Sponsorship

Your support helps us continue developing and maintaining this tool. Consider sponsoring us through:

- [GitHub Sponsors](https://github.com/sponsors/your_github_username)
- [Patreon](https://www.patreon.com/crewbrainai)

### Community Support

- [Open an issue](https://github.com/your_github_username/repo_name/issues) for bug reports or feature requests
- [Start a discussion](https://github.com/your_github_username/repo_name/discussions) to ask questions or share ideas

### Professional Services

Need expert help with your AI and project development needs? We're here to assist you:

- **AI Integration**: Let us help you integrate AI into your existing projects or develop new AI-powered solutions.
- **Custom Development**: We can tailor Code Compiler to your specific needs or create custom tools for your workflow.
- **Consulting**: Get expert advice on code analysis, AI implementation, and software architecture.

Contact us at david@crewbrain.ai for professional services or to discuss your project requirements.

### Spread the Word

Help us grow by sharing the Code Compiler with your network:

- Star the repository on GitHub
- Share your experience on social media (Twitter, LinkedIn, etc.)
- Write a blog post about how you use the tool in your workflow

Your support, whether through sponsorship, community involvement, or spreading the word, is crucial for the continued development and improvement of this project. Thank you for being part of our community!

[![Patreon](https://img.shields.io/badge/Patreon-F96854?style=for-the-badge&logo=patreon&logoColor=white "crewbrainai")](https://www.patreon.com/crewbrainai)
