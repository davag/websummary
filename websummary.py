import os
import requests
import json
from typing import List
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display, update_display
# If using official openai library:
# import openai

###############################################################################
# Initialize and constants
###############################################################################
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if api_key and api_key.startswith('sk-proj-'):
    print("API key looks good so far")
else:
    print("There might be a problem with your API key? ")

MODEL = 'gpt-4o-mini'

# If using an official OpenAI library, it might look like:
# openai.api_key = api_key
# But if you have a custom OpenAI() class, adjust accordingly:
from openai import OpenAI
openai = OpenAI()

###############################################################################
# A class to represent a Webpage
###############################################################################
class Website:
    """
    A utility class to represent a Website that we have scraped, now with links.
    """

    def __init__(self, url: str):
        self.url = url
        response = requests.get(url)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')

        # Title
        self.title = soup.title.string if soup.title else "No title found"

        # Text: remove scripts, styles, images, etc. from the body
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""

        # Links
        links = [link.get('href') for link in soup.find_all('a')]
        self.links = [link for link in links if link]

    def get_contents(self) -> str:
        return (
            f"Webpage Title:\n{self.title}\n"
            f"Webpage Contents:\n{self.text}\n\n"
        )

###############################################################################
# Prompts and message-building
###############################################################################
link_system_prompt = (
    "You are provided with a list of links found on a webpage. "
    "You are able to decide which of the links would be most relevant to include "
    "in a brochure about the company, such as links to an About page, or a Company "
    "page, or Careers/Jobs pages.\n"
    "You should respond in JSON as in this example:\n\n"
    "{\n"
    '    "links": [\n'
    '        {"type": "about page", "url": "https://full.url/goes/here/about"},\n'
    '        {"type": "careers page", "url": "https://another.full.url/careers"}\n'
    "    ]\n"
    "}\n"
)

def get_links_user_prompt(website: Website) -> str:
    user_prompt = (
        f"Here is the list of links on the website of {website.url} - please decide "
        "which of these are relevant web links for a brochure about the company, "
        "respond with the full https URL in JSON format. "
        "Do not include Terms of Service, Privacy, or email links.\n"
        "Links (some might be relative links):\n"
    )
    user_prompt += "\n".join(website.links)
    return user_prompt

###############################################################################
# Functions to retrieve links from a site, then retrieve additional pages
###############################################################################
def get_links(url: str) -> dict:
    website = Website(url)
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(website)}
        ],
        # If your custom OpenAI class supports a 'response_format' parameter:
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    return json.loads(result)

def get_all_details(url: str) -> str:
    result = "Landing page:\n"
    main_site = Website(url)
    result += main_site.get_contents()

    links = get_links(url)
    print("Found links:", links)

    # The returned dict should be of the form {"links": [{"type": "...", "url": "..."}]}
    for link_entry in links.get("links", []):
        page_type = link_entry.get("type", "")
        link_url = link_entry.get("url", "")
        result += f"\n\n{page_type}\n"
        result += Website(link_url).get_contents()

    return result

###############################################################################
# System prompt for final brochure
###############################################################################
system_prompt = (
    "You are an assistant that analyzes the contents of several relevant pages "
    "from a company website and creates a short brochure about the company for "
    "prospective customers, investors, and recruits. Respond in markdown. "
    "Include details of company culture, customers, and careers/jobs if available."
)

# If you prefer a humorous tone, uncomment:
# system_prompt = (
#     "You are an assistant that analyzes the contents of several relevant pages "
#     "from a company website and creates a short humorous, entertaining, jokey "
#     "brochure about the company for prospective customers, investors, and recruits. "
#     "Respond in markdown. Include details of company culture, customers, and careers/jobs."
# )

###############################################################################
# Functions to generate the final brochure
###############################################################################
def get_brochure_user_prompt(company_name: str, url: str) -> str:
    user_prompt = (
        f"You are looking at a company called: {company_name}\n"
        "Here are the contents of its landing page and other relevant pages; use this "
        "information to build a short brochure of the company in markdown.\n"
    )
    details = get_all_details(url)
    
    # Truncate details if necessary
    details = details[:20_000]  # adjust if your model or environment has a smaller token limit
    user_prompt += details

    return user_prompt

def create_brochure(company_name: str, url: str):
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
        ],
    )
    result = response.choices[0].message.content
    return result

def stream_brochure(company_name: str, url: str):
    """
    Example of streaming tokens as they come in.
    You may need to confirm that your environment supports streaming responses.
    """
    stream = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
        ],
        stream=True
    )
    response = ""
    display_handle = display(Markdown(""), display_id=True)
    
    for chunk in stream:
        if "choices" in chunk and chunk.choices and "delta" in chunk.choices[0]:
            content_piece = chunk.choices[0].delta.get("content", "")
            response += content_piece
            # Optionally strip markdown fences for smoother streaming display
            response_stripped = response.replace("```", "").replace("markdown", "")
            update_display(Markdown(response_stripped), display_id=display_handle.display_id)

import argparse

def create_brochure(company_name, url):
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
          ],
    )
    result = response.choices[0].message.content
    display(Markdown(result))

def render_for_web(markdown_content: str) -> str:
    """
    Convert Markdown content to HTML for use in a web app.
    """
    from markdown2 import markdown
    return markdown(markdown_content)

def render_in_terminal(markdown_content: str):
    """
    Render Markdown content for the terminal using rich (if available),
    or simply print it.
    """
    try:
        from rich.console import Console
        from rich.markdown import Markdown
        console = Console()
        console.print(Markdown(markdown_content))
    except ImportError:
        # Fallback to plain print if `rich` is not installed
        print("Markdown rendering in plain text:\n")
        print(markdown_content)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate a company brochure.")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--url", required=True, help="Company website URL")
    args = parser.parse_args()

    # Generate brochure
    markdown_brochure = create_brochure(args.company, args.url)

    # Render for terminal during development
    render_in_terminal(markdown_brochure)

    # Optionally, save to a file for debugging
    with open("brochure.md", "w") as f:
        f.write(markdown_brochure)
        print("Brochure saved to brochure.md")



if __name__ == "__main__":
    main()

