# 🧊 CREWBRAIN Code Compiler

**Download and Compile a Full Codebase Dump Report for any GitHub repo or folder.**

This script will compile a codebase and generate a report in markdown including each file. It will also count the number of tokens in the codebase. The output is in markdown format and perfectly formatted to be dropped into your favorite long context LLM for analysis.

It's a great way to explore and understand a codebase and has inadvertenly become a great way tool to archive our own codebase, and other open source projects not on github. It's also a great way to understand the complexity of a codebase and to identify potential security risks.

More planned features coming soon! Feel free to contribute to the project or contact us to work with us!

David Tapang / david@crewbrain.ai / CREWBRAIN.AI

## Features

- Analyze local directories or GitHub repositories
- Generate comprehensive reports in markdown format
- Count lines, functions, classes, methods, and variables in each file
- Calculate token counts for compatibility with large language models
- Exclude specific folders and file types from analysis
- Customizable report types
- API endpoint for remote analysis requests

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

Run the script using Python:
