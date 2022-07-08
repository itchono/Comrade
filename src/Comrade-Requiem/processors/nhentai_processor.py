import cloudscraper
from bs4 import BeautifulSoup
import re
from dis_snek.models.discord import Embed
from dataclasses import dataclass


@dataclass
class NHentaiSearchResult:
    query: str
    sort_suffix: str
    num_results: int
    num_pages: int
    cached_pages: "dict[int, list]"
    # Caches gallery numbers for each page of results
    page_cursor: int = 0
    page_subcursor: int = 0
    # Cursor position tracks which result we're on in the search results
    error: Exception = None


@dataclass
class NHentaiSession:
    # User inputs
    gallery_id: int  # Gallery ID

    # State variables
    title: str = None
    gallery_internal_id: int = 0  # Gallery internal ID
    exists: bool = True  # Whether this gallery exists or not
    current_page_number: int = 0  # Page number
    length: int = 0  # Length of gallery
    pages: "list[NHentaiPage]" = None
    error: Exception = None  # Error if one occurred


@dataclass
class NHentaiPage:
    direct_url: str
    file_extension: str


def initialize_session(gallery_id: int) -> NHentaiSession:
    '''
    Initialize session using a gallery ID
    '''
    scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance

    query_url = f"https://nhentai.net/g/{gallery_id}/"

    try:
        result = scraper.get(query_url)
    except Exception as e:
        return NHentaiSession(gallery_id=gallery_id, exists=False, error=e)

    # Parse the result using BeautifulSoup
    soup = BeautifulSoup(result.text, "html.parser")

    # The title will be the third <meta> tag on the page.
    title = soup.find_all("meta")[2]["content"]

    # The internal gallery ID is found using the fourth <meta> tag on the page.
    # The link has format https://t.nhentai.net/galleries/######/cover.<EXT>
    # Extract the number from the link using regex
    internal_gallery_id = int(re.search(
        r"galleries/(\d+)/cover", soup.find_all("meta")[3]["content"]).group(1))

    # Infer length of gallery from the number of pages
    pattern = r">(\d+)</span></a></span></div><div class=\"tag-container field-name\">[\n\r\s]+Uploaded:"
    length = int(re.search(pattern, result.text).group(1))

    # Locate all pages in the gallery
    # Pages are linked using <noscript> tags
    file_extensions = []
    for match in soup.find_all("noscript"):
        pattern = r"galleries/(\d+)/.*?\.(.*?)\""
        result = re.search(pattern, str(match))
        if result.group(1) == str(internal_gallery_id) and "cover" not in result.group(0):
            file_extensions.append(result.group(2))

    pages = [NHentaiPage(
        direct_url=f"https://i.nhentai.net/galleries/{internal_gallery_id}/{i+1}.{file_extensions[i]}",
        file_extension=file_extensions[i]) for i in range(length)]

    return NHentaiSession(gallery_id=gallery_id,
                          title=title,
                          gallery_internal_id=internal_gallery_id,
                          current_page_number=0,
                          length=length,
                          pages=pages)


def nhentai_search(query: str, mode: str = "recent") -> NHentaiSearchResult:
    '''
    Search for a gallery using a query
    '''
    scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance

    sort_suffixes = {"recent": "", "popular": "&sort=popular"}

    query_url = f"https://nhentai.net/search/?q={query}" + sort_suffixes[mode]

    try:
        result = scraper.get(query_url)
    except Exception as e:
        return NHentaiSearchResult(query=query, num_results=0, error=e,
                                   sort_suffix="", num_pages=0, cached_pages={})

    soup = BeautifulSoup(result.text, "html.parser")
    title_block = soup.find_all("h1")[0].text

    if "no" in result:
        return NHentaiSession(gallery_id=0, exists=False)

    # parse number of results as int
    # String is of format e.g. "1,780 results"
    num_results = int(
        re.search(r"(\d+)", title_block.replace(",", "")).group(1))

    # Infer number of pages from number of results
    # Each page holds approximately 25 results
    num_pages = num_results // 25 + 1

    # Cache the first page since we're already on it
    # Search for all gallery links
    gallery_numbers = re.findall(r"/g/(\d+)/", result.text)

    return NHentaiSearchResult(query=query, sort_suffix=sort_suffixes[mode], num_results=num_results,
                               num_pages=num_pages, cached_pages={0: gallery_numbers})


def nhentai_search_cursor(search_result: NHentaiSearchResult) -> NHentaiSession:
    '''
    Return an Nhentai gallery from a search result given the cursor position.
    '''
    if search_result.page_cursor in search_result.cached_pages:
        gallery_id = search_result.cached_pages[search_result.page_cursor][search_result.page_subcursor]
        return initialize_session(gallery_id)
    else:
        # Need to cache this page
        query_url = f"https://nhentai.net/search/?q={search_result.query}" + \
            search_result.sort_suffix + f"&page={search_result.page_cursor+1}"

        scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
        result = scraper.get(query_url)
        gallery_numbers = re.findall(r"/g/(\d+)/", result.text)
        search_result.cached_pages[search_result.page_cursor] = gallery_numbers
        # Update the list

        gallery_id = gallery_numbers[search_result.page_subcursor]
        return initialize_session(gallery_id)


def cover_page_embed(session: NHentaiSession) -> Embed:
    '''
    Return embed code for the cover page of the gallery
    '''
    embed = Embed(title=session.title + f" ({session.gallery_id})",
                  url=f"https://nhentai.net/g/{session.gallery_id}/",
                  color=0xfecbed,
                  image=session.pages[0].direct_url)
    embed.set_footer(text=f"Number of Pages: {session.length}")
    embed.set_author(name="NHentai", url="https://nhentai.net/")
    return embed


if __name__ == "__main__":
    # Testing script
    # result = initialize_session(185217)
    # print(result.pages)
    nhentai_search("alp")
