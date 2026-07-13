# mcp server that fetches and cleans up job posting pages
# this is the "tool" my agent will call later instead of scraping directly itself

from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup

# this creates the server and gives it a name
mcp = FastMCP("job-posting-server")


def clean_html_text(raw_html: str) -> str:
    # shared helper - takes raw html and returns just the readable text
    soup = BeautifulSoup(raw_html, "html.parser")

    # rip out stuff that's never actually part of the job description
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)


@mcp.tool()
def get_job_posting(url: str = "", pasted_text: str = "") -> str:
    """
    gets a job posting either by fetching a url or from text the user pasted in directly.
    pass EITHER url OR pasted_text, not both.

    use pasted_text when the site can't be scraped (like linkedin, which requires login) -
    the user just copy/pastes the job description text themselves instead
    """
    # if they gave pasted text, just clean it up a tiny bit and return it, no scraping needed
    if pasted_text.strip():
        lines = [line.strip() for line in pasted_text.split("\n") if line.strip()]
        return "\n".join(lines)[:8000]

    if not url.strip():
        return "error: need either a url or pasted_text"

    try:
        # pretend to be a normal browser so some sites don't block the request
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        cleaned = clean_html_text(response.text)

        # quick check - if this looks like a login wall, warn instead of returning garbage
        login_flags = ["sign in", "log in", "join now", "forgot password"]
        lowered = cleaned.lower()
        if any(flag in lowered for flag in login_flags) and len(cleaned) < 2000:
            return (
                "error: this page looks like a login wall, not a job posting. "
                "sites like linkedin require login to view postings - try pasting "
                "the job description text directly instead"
            )

        # job postings can be huge, cap it so we don't blow up token limits later
        return cleaned[:8000]

    except Exception as e:
        return f"couldn't fetch that page: {e}"


# this actually starts the server so it can be used
if __name__ == "__main__":
    mcp.run()
