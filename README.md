
# PyAirbyte Automated Tutorials

Script to automatically create and upload blog posts to Webflow. It was specifically designed to create PyAirbyte tutorials. It uses the OpenAI API to generate the text, and the PyAirbyte library itself to gather the source connectors configuration.

## Prerequisites

Before you begin, ensure you have met the following requirements:
* You have installed Python 3.x.

## Installation

Follow these steps to get your development environment running:

1. **Clone the repository**
   ```bash
   git clone https://github.com/airbytehq/pyairbyte-seo.git
   cd pyairbyte-seo
   ```

2. **Create a Python virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

   - On Unix or MacOS:
     ```bash
     source venv/bin/activate
     ```

4. **Install the required packages**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run the project, execute the following command in the root of your project directory:

```bash
python build_blogs.py
```

*To run the script for a specific set of sources, you can modify the list in the `sources.py` file.*

## Contributing

If you would like to contribute to this project, please fork the repository and issue a pull request with a description of your proposed changes.