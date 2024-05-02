import openai
import airbyte as ab
import requests
import os
from collections import OrderedDict
from dotenv import load_dotenv
from sources import sources

# Create a code example for the tutorial part of the blog post
def create_code_example(connector):
  source = ab.get_source(connector)
  prompt = f"Generate an example configuration based on the following JSON spec. Provide only the configuration, without explanations: {source.config_spec}"
  response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}]
  )
  config = response.choices[0].message.content.replace("json", "").replace("```", "")

  snippet = f"""pip install airbyte

            import airbyte as ab

            # Create and configure the source connector, don't forget to use your own values in the config:
            source = ab.get_source(
                {connector},
                install_if_missing=True,
                config={config}
            )

            # Verify the config and credentials:
            source.check()

            # List the available streams available for the {connector} connector:
            source.get_available_streams()

            # Select all streams to load to cache. You can also select some of them with the `select_streams()` method.
            source.select_all_streams()

            # Read into DuckDB local default cache. You could also use a custom cache here (Postgres, Snowflake, BigQuery, etc.)
            cache = ab.get_default_cache()
            result = source.read(cache=cache)

            # Read a stream from the cache into a pandas Dataframe, replace with the stream you're interested in. You can also read from the cache into SQL, or documents (for LLMs).
            df = cache["your_stream"].to_pandas()"""

  return snippet

# Generate each chapter based on prompts
def generate_blog_chapter(prompt, chat_history):
  response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[{"role": "system", "content": "You are a helpful assistant. Use clear, precise language, and limit pompous words. Use a natural tone. Prioritize substance"}] + chat_history + [{"role": "user", "content": prompt}]
  )
  return response.choices[0].message.content

def build_blog_post(chapter_prompts, conversation_history, blog_chapters, ctas):
  # Generate each chapter and update history
  for chapter, prompt in chapter_prompts.items():
    blog_chapters[chapter] = generate_blog_chapter(prompt, conversation_history)
    conversation_history.append({"role": "assistant", "content": blog_chapters[chapter]})

  blog_post = blog_chapters["introduction"] \
    + "\n\n" + blog_chapters["chapter_1"]   \
    + "\n\n" + blog_chapters["chapter_2"]   \
    + "\n\n" + ctas["docs_quickstarts_cta"] \
    + "\n\n" + blog_chapters["chapter_3"]   \
    + "\n\n" + blog_chapters["conclusion"]  \
    + "\n\n" + ctas["slack_newsletter_cta"]

  return blog_post

def upload_post_to_webflow(source_connector, blog_post_body):
  webflow_api_token = os.getenv("WEBFLOW_API_TOKEN")
  # PyAirbyte CMS Collection ID
  collection_id = "66200272dd44bc109a1d8cff"

  # URL for the Webflow API endpoint, collection items
  api_url = f'https://api.webflow.com/v2/collections/{collection_id}/items'

  headers = {
      "Authorization": f"Bearer {webflow_api_token}",
      "accept": "application/json",
      "content-type": "application/json"
  }

  # Data for the blog post
  blog_post_data = {
    "isArchived": False,
    "isDraft": True,  # Set as draft
    "fieldData": {
      "name": f"How To Create a {source_connector['original']} Python Pipeline with PyAirbyte",
      "slug": f"{source_connector['formatted'].replace('source-', '')}-python",

      # Custom Fields
      "seo-title-tag": f"How To Create a {source_connector['original']} Python Pipeline with PyAirbyte",
      "seo-meta-description": f"Learn how to create a {source_connector['original']} Python data pipeline with our easy step-by-step guide. Master the setup using PyAirbyte to efficiently manage your {source_connector['original']} data.",  # Replace with your SEO Meta Description
      "publish-date": "2024-04-24T12:00:00.000Z", 
      "time-to-read": "10 min read",
      "post-body": blog_post_body,
    }
  }

  # Make the POST request to create a new item
  response = requests.post(api_url, json=blog_post_data, headers=headers)

  # Check the response and print the result
  if response.status_code in [200, 201, 202]:
      print(f"Blog post successfully uploaded for {source_connector['original']}!")
  else:
      print(f"Failed to upload blog post {source_connector['original']}. Status code: {response.status_code}, Response: {response.text}")

def download_post(source_connector, blog_post_body):
  
  filename = f"./blogs/{source_connector['formatted']}.md"

  # Write the text to a file
  with open(filename, "w", encoding="utf-8") as file:
      file.write(blog_post_body)

  print(f"File saved as {filename}!")
  

if __name__ == "__main__":
  # Load environment variables from .env file
  load_dotenv()

  # Initialize OpenAI client with API key
  client = openai.OpenAI(api_key=os.getenv("OPENAI_KEY"))
  
  # Calls to action to include in the blog post
  ctas = {
      "docs_quickstarts_cta": "For keeping up with the latest PyAirbyte’s features, make sure to check [our documentation](https://docs.airbyte.com/using-airbyte/pyairbyte/getting-started). And if you’re eager to see more code examples with PyAirbyte, check out our [Quickstarts library](https://github.com/airbytehq/quickstarts/tree/main/pyairbyte_notebooks).",
      "slack_newsletter_cta": "Do you have any questions or feedback for us? You can keep in touch by joining our [Slack channel](https://airbyte.com/community/community)! If you want to keep up to date with new PyAirbyte features, [subscribe to our newsletter](https://airbyte.com/community/newsletter)."
  }

  for source in sources:

    # Prompts for each chapter
    chapter_prompts = OrderedDict([
        ("chapter_1", f"I’m writing a guide and I need your help to write some of the chapters.\r\n\r\nThe guide focuses on the challenges of creating custom Python scripts for creating data pipelines from {source['original']} and how PyAirbyte simplifies this process. \r\n\r\n[PyAirbyte] (https://airbyte.com/product/pyairbyte) is an open-source Python library that packages Airbyte connectors and makes them available as code, while removing the need for hosted services or an Airbyte Cloud account.\r\n\r\nPlease help me write the following chapter. Don’t include an introduction and conclusion:\r\n\r\nTitle: Traditional Methods for Creating {source['original']} Data Pipelines\r\nCover the following:\r\nOutline conventional methods, like custom Python scripts.\r\nDescribe specific pain points in extracting data from {source['original']}.\r\nExplain the impact of these challenges on data pipeline efficiency and maintenance.\r\n"),
        ("chapter_2", f"Let’s continue with the next chapter. Don’t include an introduction and conclusion:\r\n\r\nTitle: Implementing a Python Data Pipeline for {source['original']} with PyAirbyte\r\nInclude the following Python code snippets and explain what’s happening in each section:\r\n{create_code_example(source['formatted'])}\r\n"),
        ("chapter_3", f"Let’s continue with the next chapter. Don’t include an introduction and conclusion:\r\n\r\nTitle: Why Using PyAirbyte for {source['original']} Data Pipelines:\r\nCover the following:\r\nPyAirbyte can be installed with pip, and the only requirement is to have Python installed.\r\nYou can easily get and configure the available source connectors. It’s also possible to install custom source connectors.\r\nBy enabling the selection of specific data streams, PyAirbyte conserves computing resources and streamlines data processing.\r\nWith support for multiple caching backends like DuckDB, MotherDuck, Postgres, Snowflake and BigQuery, PyAirbyte offers flexibility. If users don’t define a specific Cache, DuckDB is used as the default cache.\r\nPyAirbyte is able to read data incrementally. This feature is key for efficiently handling large datasets and reducing the load on data sources.\r\nPyAirbyte is compatible with various Python libraries, like Pandas and SQL-based tools, which opens up a wide range of possibilities for data transformation, analysis, integration into existing Python-based data workflows, orchestrators and AI frameworks.\r\nPyAirbyte is ideally suited for enabling AI applications.\r\n"),
        ("conclusion", f"Let’s write a very short conclusion chapter for this guide."),
        ("introduction", f"Let’s write a very short introduction, highlighting some of the challenges and how PyAirbyte could reduce them."),
    ])

    # Initialize the conversation history
    conversation_history = []

    # Initialize dictionary to hold chapter contents
    blog_chapters = {}

    # Generate the blog post
    blog_post = build_blog_post(chapter_prompts, conversation_history, blog_chapters, ctas)

    # Download post locally
    download_post(source, blog_post)

    # Upload blog post to Webflow
    upload_post_to_webflow(source, blog_post)