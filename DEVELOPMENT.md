# Development Environment Setup

This document outlines the tools and environment required to work with the Physical AI & Humanoid Robotics textbook project.

## Required Tools

### Core Tools
- **Node.js** (v18.0 or higher) - For running Docusaurus
- **npm** or **yarn** - Package manager for Docusaurus dependencies
- **Git** - Version control for the textbook content
- **A modern text editor** (VS Code recommended) with Markdown support

### Optional Tools for Enhanced Development
- **Python 3.x** - For running code examples and simulations
- **ROS2** - For robotics-specific examples (Humble Hawksbill or later recommended)
- **Isaac Sim** - For simulation examples (NVIDIA Omniverse)
- **LaTeX** - For PDF generation from Markdown
- **Docker** - For consistent development environments

## Installation Steps

### 1. Install Node.js and npm
- Download from [nodejs.org](https://nodejs.org/)
- Verify installation: `node --version` and `npm --version`

### 2. Install Git
- Download from [git-scm.com](https://git-scm.com/)
- Verify installation: `git --version`

### 3. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 4. Install Docusaurus Dependencies
```bash
npm install
```

### 5. Start Development Server
```bash
npm start
```

## Recommended VS Code Extensions
- **Markdown All in One** - Enhanced Markdown editing
- **GitHub Markdown Preview** - Preview Markdown files
- **Prettier** - Code formatting
- **ESLint** - JavaScript/TypeScript linting (for Docusaurus config)

## Python Environment (Optional)
If working with Python examples:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install numpy matplotlib
```

## Docusaurus Commands Reference
- `npm start` - Start local development server
- `npm run build` - Build static website
- `npm run serve` - Serve built website locally
- `npm run deploy` - Deploy to GitHub Pages

## Troubleshooting
- If you encounter build errors, try clearing Docusaurus cache: `npx docusaurus clear`
- Ensure you're using a supported Node.js version (check Docusaurus documentation)
- For Isaac Sim examples, ensure you have a compatible GPU and drivers installed

## Development Workflow
1. Create a new branch for content changes
2. Make changes to Markdown files in the `/docs` directory
3. Preview changes with `npm start`
4. Commit changes with descriptive commit messages
5. Push branch and create a pull request for review