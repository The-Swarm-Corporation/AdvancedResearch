# Advanced Research Examples

This directory contains comprehensive examples demonstrating how to use the Advanced Research system. All examples are designed to be simple and easy to understand, with no print statements.

## 📚 Available Examples

### Basic Examples

- **[`basic_usage.py`](basic_usage.py)** - Simple research with minimal configuration
- **[`export_example.py`](export_example.py)** - How to use export functionality
- **[`chat_demo.py`](chat_demo.py)** - Interactive chat interface demo

### Configuration Examples

- **[`advanced_config.py`](advanced_config.py)** - Advanced configuration options
- **[`custom_models.py`](custom_models.py)** - Different model configurations
- **[`output_formats.py`](output_formats.py)** - Various output format options

### Advanced Features

- **[`batch_processing.py`](batch_processing.py)** - Process multiple queries in batch
- **[`multi_loop_research.py`](multi_loop_research.py)** - Iterative research with multiple loops
- **[`session_management.py`](session_management.py)** - Session tracking and conversation management

## 🚀 Quick Start

To run any example:

```bash
# Basic research
python examples/basic_usage.py

# With export functionality
python examples/export_example.py

# Advanced configuration
python examples/advanced_config.py
```

## 🔧 Prerequisites

Before running the examples, make sure you have:

1. **Installed the package**: `pip install advanced-research`
2. **Set up API keys** in environment variables:
   - `EXA_API_KEY` (required for web search)
   - `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` (for LLM functionality)

## 📖 Example Categories

### **Basic Research**
Start with `basic_usage.py` to understand the fundamental workflow.

### **Export & Persistence**
Use `export_example.py` to learn how to save research results to JSON files.

### **Model Configuration**
Explore `custom_models.py` to see how to configure different AI models.

### **Output Formats**
Check `output_formats.py` to understand JSON, markdown, and conversation history outputs.

### **Batch Processing**
Use `batch_processing.py` for processing multiple research tasks efficiently.

### **Multi-Loop Research**
Learn iterative research with `multi_loop_research.py`.

### **Session Management**
Understand conversation tracking with `session_management.py`.

## 🎯 Use Cases

These examples cover common research scenarios:

- **Academic Research** - Literature reviews and topic exploration
- **Business Intelligence** - Market research and competitive analysis
- **Technical Research** - Technology trends and implementation strategies
- **Scientific Research** - Current developments and breakthroughs
- **Content Creation** - Research for articles, reports, and presentations

## 🔍 Customization

Each example can be customized by:

- Changing the research query
- Adjusting model parameters
- Modifying output formats
- Enabling/disabling export functionality
- Adjusting the number of research loops

## 📝 Notes

- All examples return results rather than printing them
- Examples are designed to be run independently
- Each example demonstrates a specific feature or use case
- Results can be stored in variables for further processing
- Export examples automatically save results to timestamped JSON files

## 🤝 Contributing

Feel free to create additional examples or modify existing ones to suit your specific needs. Each example should:

- Be self-contained and runnable
- Demonstrate a clear use case
- Use descriptive variable names
- Include helpful comments
- Return results instead of printing them
