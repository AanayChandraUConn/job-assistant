# mcp server that fetches and cleans up job posting pages
# this is the "tool" my agent will call later instead of scraping directly itself

from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup

# this creates the server and gives it a name
mcp = FastMCP("job-posting-server")

@mcp.tool()
def fetch_job_posting(url: str) -> str:
    """
    grabs a job posting page and pulls out just the readable text,
    stripping out nav bars, scripts, footers etc that we don't care about
    """
    try:
        # pretend to be a normal browser so some sites don't block the request
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # rip out stuff that's never actually part of the job description
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # get_text just grabs whatever text is left after removing that junk
        text = soup.get_text(separator="\n")

        # collapse a bunch of blank lines into single ones, makes it way more readable
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        cleaned = "\n".join(lines)

        # job postings can be huge, cap it so we don't blow up token limits later
        return cleaned[:8000]

    except Exception as e:
        return f"couldn't fetch that page: {e}"

# this actually starts the server so it can be used
if __name__ == "__main__":
    mcp.run()
