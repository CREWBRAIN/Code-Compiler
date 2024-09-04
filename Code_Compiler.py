"""
🧊 CREWBRAIN Code Compiler - Download and Compile a Full Codebase Dump Report for any repo or folder.
    This script will compile a codebase and generate a report of the number of lines, functions, 
    classes, methods, and variables in each file. It will also count the number of tokens in the 
    codebase. The output is in markdown format and perfectly formatted to be dropped into your
    favorite long context LLM for analysis.

    It's a great way to explore and understand a codebase and has inadvertenly become a great way tool
    to archive our own codebase, and other open source projects not on github.
    It's also a great way to understand the complexity of a codebase and to identify potential 
    security risks.

    There's also a flask api server built in to host the report on your local machine.

    More planned features coming soon! Feel free to contribute to the project or contact us to work with us!

    David Tapang / david@crewbrain.ai / CREWBRAIN.AI

"""

import os
import re
import sys
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator
from collections import Counter
from flask import Flask, jsonify, request
from git import RemoteProgress
import git
import yaml
import tiktoken
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()

DEFAULT_CONFIG = {
    "supported_types": [".py", ".ts", ".js", ".md", ".txt"],
    "include_folders": [],
    "exclude_folders": [".git", "node_modules", "venv", "__pycache__", ".venv"],
    "max_file_size": 1000000,  # 1 MB
    "report_types": {
        "1": {
            "name": "All Supported File Types",
            "file_types": ["py", "ts", "js", "md", "txt"]
        },
        "2": {
            "name": "Python, TypeScript, JavaScript",
            "file_types": ["py", "ts", "js"]
        }
    },
    "results_dir": "output",
    "repo_dir": "repos"
}

class GitProgress(RemoteProgress):
    """
    This class is used to display the progress of the GitHub repository downloader.
    """
    def __init__(self):
        super().__init__()
        self.pbar = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        self.task = self.pbar.add_task("[cyan]Downloading...", total=100)
        self.base_directory = None
        self.download_speed = 0

    def update(self, op_code, cur_count, max_count=None, message=''):
        if max_count is not None:
            self.pbar.update(self.task, completed=cur_count * 100 / max_count)
        self.pbar.refresh()

    def __enter__(self):
        self.pbar.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pbar.stop()

class CodeCompiler:
    """
    This class is used to compile the codebase of a given directory or GitHub repository.
    It can generate reports in different formats based on the configuration.
    """
    def __init__(self, config_path: str, logger: logging.Logger):
        self.logger = logger
        self.config_path = config_path
        self.config = self.load_config()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        self.base_directory = None

    def load_config(self) -> Dict[str, Any]:
        """
        This method is used to load the configuration from the config file.
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            self.logger.warning(
                f"Config file not found at {self.config_path}. Using default configuration."
            )
            return DEFAULT_CONFIG
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML configuration: {e}")
            return DEFAULT_CONFIG

    def save_config(self):
        """
        This method is used to save the configuration to the config file.
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file)
            console.print(Panel(f"Configuration saved to {self.config_path}", style="green"))
        except OSError as e:
            self.logger.error(f"Error saving configuration: {e}")
            console.print(Panel(f"Error saving configuration: {e}", style="bold red"))

    def read_file_content(self, file_path: Path) -> str:
        """
        This method is used to read the content of a file.
        """
        if not file_path.is_file():
            self.logger.warning(f"Not a file: {file_path}")
            return ""

        if file_path.stat().st_size > self.config['max_file_size']:
            self.logger.warning(f"File {file_path} exceeds max size limit. Skipping.")
            return ""

        content = ""
        encodings = ['utf-8', 'latin-1', 'ascii']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read()
                    break
            except UnicodeDecodeError:
                continue
            except OSError as e:
                self.logger.error(f"Error reading file {file_path}: {str(e)}")
                return ""

        if content:
            token_count = self.count_tokens(content)
            if token_count > self.config.get('max_token_count', float('inf')):
                self.logger.warning(f"File {file_path} exceeds max token count limit. Skipping.")
                return ""

        return content

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        This method is used to analyze a file and return its content, line count, character count, 
        function count, class count, method count, variable count, and comment count.
        """
        content = self.read_file_content(file_path)
        if not content:
            return {}
        lines = content.split('\n')
        return {
            'file': str(file_path),
            'language': file_path.suffix[1:],
            'content': content,
            'lines': len(lines),
            'characters': len(content),
            'functions': len(re.findall(r'\bdef\s+\w+\s*\(', content)),
            'classes': len(re.findall(r'\bclass\s+\w+', content)),
            'methods': len(re.findall(r'\bdef\s+\w+\s*\(self', content)),
            'variables': len(re.findall(r'\b\w+\s*=', content)),
            'comments': len([line for line in lines if line.strip().startswith('#')])
        }

    def should_include_path(self, path: Path) -> bool:
        """
        This method is used to determine if a path should be included in the analysis.
        """
        try:
            relative_path = path.relative_to(self.base_directory)
        except ValueError:
            self.logger.warning(
                f"Path {path} is not relative to base directory {self.base_directory}"
            )
            return False

        path_parts = relative_path.parts

        # Check if path is in excluded folder
        if any(excluded in path_parts for excluded in self.config['exclude_folders']):
            return False

        # If include_folders is empty, include all folders except excluded ones
        if not self.config['include_folders']:
            return True

        # Check if path is in included folder
        return any(included in path_parts for included in self.config['include_folders'])

    def scan_directory(self, directory: Path) -> Generator[Path, None, None]:
        """
        This method is used to scan a directory and its subdirectories for supported files.
        """
        try:
            for item in directory.iterdir():
                if item.is_dir() and self.should_include_path(item):
                    self.logger.info(f"Scanning directory: {item}")
                    yield from self.scan_directory(item)
                elif (item.is_file() and
                      item.suffix in self.config['supported_types'] and
                      self.should_include_path(item)):
                    self.logger.info(f"Found file: {item}")
                    yield item
        except PermissionError:
            self.logger.warning(f"Permission denied: unable to access {directory}")
        except OSError as e:
            self.logger.error(f"Error scanning directory {directory}: {str(e)}")

    def compile_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """
        This method is used to compile a directory and return a list of file analysis results.
        """
        results = []
        files = list(self.scan_directory(directory))
        total_files = len(files)
        
        self.logger.info(f"Found {total_files} files to analyze")
        
        analyze_task = self.progress.add_task("[cyan]Analyzing files...", total=total_files)
        
        for file_path in files:
            file_analysis = self.analyze_file(file_path)
            if file_analysis:
                results.append(file_analysis)
                self.logger.info(f"Analyzed file: {file_path}")
            else:
                self.logger.warning(f"Failed to analyze file: {file_path}")
            self.progress.update(analyze_task, advance=1)
        
        self.progress.remove_task(analyze_task)
        self.logger.info(f"Completed analysis. Found {len(results)} valid files.")
        return results

    def count_tokens(self, text: str) -> int:
        """
        This method is used to count the number of tokens in the given text.
        """
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(encoding.encode(text, disallowed_special=()))

    def generate_report(self, results: List[Dict[str, Any]], directory_name: str, report_type: int) -> str:
        """
        This method is used to generate a report for the given list of file analysis results.
        """
        self.logger.info(f"Generating report for {len(results)} files")
        
        # Add README.md content at the top of the report
        readme_content = self.get_readme_content(self.base_directory)
        report = f"# Project: {directory_name}\n\n"
        if readme_content:
            report += f"## README\n\n{readme_content}\n\n"
        
        report += "## Codebase Overview\n\n"
        
        # Add total token count
        total_tokens = sum(self.count_tokens(result['content']) for result in results)
        report += f"Total Tokens: {total_tokens}\n\n"
        
        # Add file type counts
        file_type_counts = Counter(result['language'] for result in results)
        report += "### File Type Counts:\n"
        
        report_config = self.config['report_types'].get(str(report_type))
        if not report_config:
            self.logger.error(f"Report type {report_type} not found in configuration")
            return f"Error: Report type {report_type} not found in configuration"
        
        file_types = report_config.get('file_types', [])
        
        self.logger.info(f"File types in config: {file_types}")
        self.logger.info(f"File types found: {list(file_type_counts.keys())}")
        
        for file_type in file_types:
            count = file_type_counts.get(file_type, 0)
            report += f"{file_type.capitalize()}: {count}\n"
            self.logger.info(f"Adding to report: {file_type.capitalize()}: {count}")
        
        # Add directory structure
        report += "\n## Directory Structure\n"
        report += self.generate_directory_structure(self.base_directory)
        
        # Add detailed file contents
        report += "\n## Detailed File Contents\n"
        report_task = self.progress.add_task("[cyan]Generating report...", total=len(results))
        
        for file_type in file_types:
            report += f"\n## {file_type.capitalize()} File by File\n"
            file_count = 0
            total_files = sum(1 for result in results if result['language'] == file_type)
            for result in results:
                if result['language'] == file_type:
                    file_count += 1
                    file_tokens = self.count_tokens(result['content'])
                    report += (
                        f"### {file_count}/{total_files}: {result['file']} {result['language']} "
                        f"[{result['lines']} {result['characters']} {result['functions']} "
                        f"{result['classes']} {result['methods']} {result['variables']} "
                        f"{result['comments']} | Tokens: {file_tokens}]\n"
                    )
                    report += f"```{result['language']}\n{result['content']}\n```\n\n"
                self.progress.update(report_task, advance=1)
        
        self.progress.remove_task(report_task)
        
        self.logger.info(f"Report generated with {len(report.splitlines())} lines and {total_tokens} tokens")
        return report

    def run_report(self, source: str, report_type: int) -> None:
        """
        This method is used to run the report for the given source and report type.
        """
        # Step 1: Determine the directory to analyze
        if source.startswith(("http://", "https://")):
            console.print("[bold cyan]Downloading repository...[/bold cyan]")
            directory_path = self.download_github_repo(source)
            if not directory_path:
                self.logger.error("Failed to download repository")
                return
        else:
            directory_path = Path(source)

        if not directory_path.is_dir():
            self.logger.error(f"Invalid directory: {directory_path}")
            console.print(Panel(f"Invalid directory: {directory_path}", style="bold red"))
            
            # Attempt to download the repository if the directory is invalid
            if source.startswith(("http://", "https://")):
                console.print("[bold cyan]Attempting to download repository...[/bold cyan]")
                directory_path = self.download_github_repo(source)
                if not directory_path:
                    self.logger.error("Failed to download repository after invalid directory")
                    return
            else:
                return

        # Step 2: Compile the directory
        console.print("[bold cyan]Analyzing files...[/bold cyan]")
        self.base_directory = directory_path
        results = self.compile_directory(directory_path)

        # Step 3: Generate the report
        if results:
            self.logger.info(f"Passing {len(results)} results to generate_report")
            console.print("[bold cyan]Generating report...[/bold cyan]")
            report = self.generate_report(results, directory_path.name, report_type)
            self.logger.info(f"Generated report has {len(report.splitlines())} lines")

            # Step 4: Save the report
            console.print("[bold cyan]Saving report...[/bold cyan]")
            self.save_report(report, directory_path.name, report_type)
        else:
            self.logger.warning("No supported files found in the directory")
            console.print(Panel("No supported files found in the directory", style="yellow"))

    def save_report(self, report: str, directory_name: str, report_type: int) -> None:
        """
        This method is used to save the report to the results directory.
        """
        results_dir = Path(self.config['results_dir'])
        results_dir.mkdir(exist_ok=True)
        filename = f"{directory_name}_report_{report_type}.md"
        filepath = results_dir / filename

        save_task = self.progress.add_task("[cyan]Saving report...", total=100)
        
        try:
            with open(filepath, "w", encoding='utf-8') as f:
                f.write(report)
            self.progress.update(save_task, completed=100)
            self.logger.info(f"Report saved to {filepath}")
            console.print(Panel(f"Report saved to {filepath}", style="green"))
        except OSError as e:
            console.print(Panel(f"Error saving report: {str(e)}", style="bold red"))
        finally:
            self.progress.remove_task(save_task)

    def download_github_repo(self, url: str) -> Optional[Path]:
        """
        This method is used to download a GitHub repository to the local machine.
        """
        repo_dir = Path(self.config['repo_dir'])
        repo_dir.mkdir(exist_ok=True)
        
        # Extract repo name from URL
        repo_name = url.split('/')[-1].replace('.git', '')
        repo_path = repo_dir / repo_name
        
        try:
            self.logger.info(f"Attempting to download/update repository: {url}")
            console.print(f"Downloading/updating repository: {url}", style="yellow")
            
            if repo_path.exists():
                self.logger.info(f"Repository already exists. Updating: {repo_path}")
                console.print(f"Repository already exists. Updating: {repo_path}", style="yellow")
                repo = git.Repo(repo_path)
                origin = repo.remotes.origin
                origin.pull()
                self.logger.info(f"Updated existing repository: {repo_path}")
                console.print(f"Updated existing repository: {repo_path}", style="green")
            else:
                self.logger.info(f"Cloning new repository: {url}")
                console.print(f"Cloning new repository: {url}", style="yellow")
                with GitProgress() as progress:
                    git.Repo.clone_from(url, repo_path, progress=progress)
                self.logger.info(f"Cloned new repository: {repo_path}")
                console.print(f"Cloned new repository: {repo_path}", style="green")
            
            return repo_path
        except git.GitCommandError as e:
            self.logger.error(f"Git command error: {str(e)}")
            console.print(Panel(f"Git command error: {str(e)}", style="bold red"))
        except Exception as e:
            self.logger.error(f"Unexpected error during repository download: {str(e)}")
            console.print(Panel(f"Unexpected error during repository download: {str(e)}", style="bold red"))
        
        return None

    def get_readme_content(self, directory: Path) -> str:
        """
        This method retrieves the content of the README.md file if it exists.
        """
        readme_path = directory / "README.md"
        if readme_path.exists():
            return self.read_file_content(readme_path)
        return ""

    def generate_directory_structure(self, directory: Path, prefix: str = "") -> str:
        """
        This method generates a string representation of the directory structure.
        """
        structure = ""
        items = sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name))
        for index, item in enumerate(items):
            if item.name in self.config['exclude_folders']:
                continue
            is_last = index == len(items) - 1
            structure += f"{prefix}{'└── ' if is_last else '├── '}{item.name}\n"
            if item.is_dir():
                structure += self.generate_directory_structure(
                    item, 
                    prefix + ('    ' if is_last else '│   ')
                )
        return structure

def setup_logging(log_file: str) -> logging.Logger:
    """
    This function is used to set up logging for the code compiler.
    """
    logger = logging.getLogger("Code_Compiler")
    logger.setLevel(logging.DEBUG)
    
    # Create the log directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    os.makedirs(log_dir, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def display_menu(config: Dict[str, Any]) -> str:
    """
    This function is used to display the main menu of the code compiler.
    """
    console.print("\n[bold cyan]🧊 CREWBRAIN Code Compiler[/bold cyan]")
    
    for report_type, report_config in config['report_types'].items():
        console.print(f"{report_type}. Generate Report: {report_config['name']}")
    
    settings_option = len(config['report_types']) + 1
    exit_option = settings_option + 1
    api_option = exit_option + 1
    
    console.print(f"{settings_option}. Settings")
    console.print(f"{api_option}. Start API Server")
    console.print(f"{exit_option}. Exit")
    
    choices = [str(i) for i in range(1, api_option + 1)]
    return Prompt.ask(
        f"Choose an option [{'/'.join(choices)}]",
        choices=choices,
        default=str(exit_option)
    )

def display_settings_menu(config: Dict[str, Any]) -> None:
    """
    This function is used to display the settings menu of the code compiler.
    """
    while True:
        console.print("\n[bold cyan]Settings[/bold cyan]")
        console.print("1. Modify supported file types")
        console.print("2. Set include folders")
        console.print("3. Set exclude folders")
        console.print("4. Set max file size")
        console.print("5. Set max token count")
        console.print("6. Modify report types")
        console.print("7. Set results directory")
        console.print("8. Set repo directory")
        console.print("9. Back to main menu")
        
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"], default="9")
        
        if choice == "1":
            config['supported_types'] = Prompt.ask("Enter supported file types (comma-separated)").split(',')
        elif choice == "2":
            config['include_folders'] = Prompt.ask("Enter folders to include (comma-separated, leave empty for all)").split(',')
        elif choice == "3":
            config['exclude_folders'] = Prompt.ask("Enter folders to exclude (comma-separated)").split(',')
        elif choice == "4":
            config['max_file_size'] = IntPrompt.ask("Enter max file size in bytes", default=config['max_file_size'])
        elif choice == "5":
            config['max_token_count'] = IntPrompt.ask("Enter max token count", default=config.get('max_token_count', 10000))
        elif choice == "6":
            modify_report_types(config)
        elif choice == "7":
            config['results_dir'] = Prompt.ask("Enter results directory", default=config['results_dir'])
        elif choice == "8":
            config['repo_dir'] = Prompt.ask("Enter repo directory", default=config['repo_dir'])
        elif choice == "9":
            break

def modify_report_types(config: Dict[str, Any]) -> None:
    """
    This function is used to modify the report types of the code compiler.
    """
    while True:
        console.print("\nCurrent Report Types:")
        for report_type, report_config in config['report_types'].items():
            console.print(f"{report_type}. {report_config['name']}: {', '.join(report_config['file_types'])}")
        
        console.print("\n1. Add new report type")
        console.print("2. Modify existing report type")
        console.print("3. Delete report type")
        console.print("4. Back to settings menu")
        
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"], default="4")
        
        if choice == "1":
            report_type = str(len(config['report_types']) + 1)
            name = Prompt.ask("Enter report name")
            file_types = Prompt.ask("Enter file types (comma-separated)").split(',')
            config['report_types'][report_type] = {"name": name, "file_types": file_types}
        elif choice == "2":
            report_type = Prompt.ask("Enter report type number to modify")
            if report_type in config['report_types']:
                name = Prompt.ask("Enter new report name (leave empty to keep current)")
                if name:
                    config['report_types'][report_type]["name"] = name
                file_types = Prompt.ask("Enter new file types (comma-separated, leave empty to keep current)")
                if file_types:
                    config['report_types'][report_type]["file_types"] = file_types.split(',')
            else:
                console.print("Invalid report type number", style="bold red")
        elif choice == "3":
            report_type = Prompt.ask("Enter report type number to delete")
            if report_type in config['report_types']:
                del config['report_types'][report_type]
            else:
                console.print("Invalid report type number", style="bold red")
        elif choice == "4":
            break

# Initialize Flask app
app = Flask(__name__)

# Initialize CodeCompiler globally
config_path = "Code_Compiler.yml"
log_file = "logs/Code_Compiler.log"
logger = setup_logging(log_file)
compiler = CodeCompiler(config_path, logger)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """
    API endpoint to analyze a directory or GitHub repository.
    Expects JSON with 'source' and 'report_type'.
    """
    data = request.json
    source = data.get('source')
    report_type = data.get('report_type')

    if not source or not report_type:
        return jsonify({"error": "Source and report_type are required."}), 400

    try:
        compiler.run_report(source, report_type)
        return jsonify({"message": "Report generated successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def main() -> None:
    """
    This function is used to run the main menu of the code compiler.
    """
    try:
        config_path = "Code_Compiler.yml"
        log_file = "logs/Code_Compiler.log"
        
        # Create the logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logger = setup_logging(log_file)
        compiler = CodeCompiler(config_path, logger)

        # INSTALL REQUIRED PACKAGES IF NOT ALREADY INSTALLED
        required_packages = {
            "rich": "rich",
            "PyYAML": "yaml",
            "tiktoken": "tiktoken",
            "GitPython": "git",
            "Flask": "flask"
        }
        for package, import_name in required_packages.items():
            try:
                __import__(import_name)
            except ImportError:
                console.print(f"Installing {package}...", style="yellow")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to install {package}: {e}")
                    console.print(f"Failed to install {package}. Please install it manually.", style="bold red")
                    continue

        while True:
            choice = display_menu(compiler.config)
            exit_option = str(len(compiler.config['report_types']) + 2)
            settings_option = str(len(compiler.config['report_types']) + 1)
            api_option = str(len(compiler.config['report_types']) + 3)  # New option for API

            if choice == exit_option or choice == "":
                console.print("Exiting 🧊 CREWBRAIN Code Compiler. Goodbye!", style="bold blue")
                break
            elif choice == settings_option:
                display_settings_menu(compiler.config)
                compiler.save_config()
            elif choice == api_option:  # Handle API option
                console.print("Starting API server...", style="bold cyan")
                app.run(debug=True)  # This will start the Flask app
            else:
                source = Prompt.ask("Enter the directory path or GitHub repository URL to analyze")
                compiler.run_report(source, int(choice))
                input("Press Enter to continue...")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        console.print(Panel(f"An unexpected error occurred: {e}", style="bold red"))

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    main()