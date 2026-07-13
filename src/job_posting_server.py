# this is my mcp server - basically a tool that claude can call to grab
# job posting text off the internet instead of me copy pasting it every time
from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup

mcp = FastMCP("job-posting-server")


def clean_html_text(raw_html: str) -> str:
    # takes raw html and just gets the actual readable text out of it
    soup = BeautifulSoup(raw_html, "html.parser")

    # get rid of stuff that's never part of the actual job description
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)


@mcp.tool()
def get_job_posting(url: str = "", pasted_text: str = "") -> str:
    """
    grabs a job posting either from a url or from text someone pasted in directly.
    give it EITHER url OR pasted_text, not both.

    pasted_text is for when the site can't be scraped (like linkedin, it makes
    you log in) - the user just copies the text themselves instead
    """
    if pasted_text.strip():
        lines = [line.strip() for line in pasted_text.split("\n") if line.strip()]
        return "\n".join(lines)[:8000]

    if not url.strip():
        return "error: need either a url or pasted_text"

    try:
        # gotta pretend to be a normal browser or some sites just block you
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        cleaned = clean_html_text(response.text)

        # if it smells like a login page instead of a job posting, say so
        # instead of just returning garbage
        login_flags = ["sign in", "log in", "join now", "forgot password"]
        lowered = cleaned.lower()
        if any(flag in lowered for flag in login_flags) and len(cleaned) < 2000:
            return (
                "error: this page looks like a login wall, not a job posting. "
                "sites like linkedin require login to view postings - try pasting "
                "the job description text directly instead"
            )

        # job postings can be long, capping it so we don't blow past token limits
        return cleaned[:8000]

    except Exception as e:
        return f"couldn't fetch that page: {e}"


if __name__ == "__main__":
    mcp.run()
