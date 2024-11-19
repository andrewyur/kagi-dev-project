from pydantic import BaseModel
import lxml.html as html
from flask import g
from openai import AsyncOpenAI
import openai
import os
import asyncio
from rss.utils import RssData


# returns the html element that has the highest number of children which are ancestors of anchor tags
def get_list_element(element: html.HtmlElement):
    if element.tag == "a":
        return (1, element)
    else:
        self_count = 0
        largest_child_count = 0
        largest_child = None

        for child_element in element:  # type: ignore
            candidate_ct, candidate = get_list_element(child_element)
            if candidate_ct > 0:
                self_count += 1
                if candidate_ct > largest_child_count:
                    largest_child_count = candidate_ct
                    largest_child = candidate

        if largest_child is None or self_count > largest_child_count:
            return (self_count, element)
        else:
            return (largest_child_count, largest_child)


# generates a css query that uniquely identifies the given element
def calculate_css_query(element: html.HtmlElement):
    path = []
    parent: html.HtmlElement | None = None

    while element.getparent() is not None:
        parent = element.getparent()

        element_index = parent.index(element, None, None)  # type: ignore

        path.insert(0, f"{element.tag}:nth-child({element_index + 1})")

        element = parent  # type: ignore

    return " > ".join(path).lower()


class Queries(BaseModel):
    item_title: str
    item_link: str
    item_description: str | None
    item_pubDate: str | None


async def generate_css_subqueries(list_html: str):

    if "openai" not in g:
        g.openai = AsyncOpenAI(api_key=os.environ.get("API_KEY"))

    client = g.openai

    completion = await client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"""Given the following HTML, identify CSS queries to select the HTML elements for the following items:
- Title (required)
- Link (required)
- Description (if available)
- Publishing Date (if available)

For each item, return a null value if it is not present.

assume that the queries you return will be prepended onto a query identifying the html snippet you were given, and used with document.querySelectorAll() to obtain a list of Html elements. If the CSS queries return lists of elements that are different lengths, the output will be rejected.

### Input HTML
{list_html}""",
            },
        ],
        response_format=Queries,
    )

    if completion.choices is None or completion.choices[0].message.parsed is None:
        return None

    return completion.choices[0].message.parsed.model_dump()


async def generate_static_info(text: str):

    if "openai" not in g:
        g.openai = AsyncOpenAI(api_key=os.environ.get("API_KEY"))

    client = g.openai

    class StaticInfo(BaseModel):
        channel_description: str
        channel_title: str

    completion = await client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"Given the following text extracted from a webpage, provide a title and brief description (20 words max) of the text in the channel_description and channel_title keys: {text}",
            },
        ],
        response_format=StaticInfo,
    )

    if completion.choices is None or completion.choices[0].message.parsed is None:
        return None

    return completion.choices[0].message.parsed.model_dump()


async def generate_rss_data(url: str, document: html.HtmlElement) -> RssData | str:

    target = None
    if len(document.cssselect("main")) > 0:
        target = document.cssselect("main")[0]
    else:
        target = document.cssselect("body")[0]

    _, list_el = get_list_element(target)

    base_query = calculate_css_query(list_el)

    list_el_str: str = html.tostring(list_el)  # type: ignore

    list_el.drop_tree()
    for item in document.cssselect("script"):
        item.drop_tree()

    relevant_text = document.text_content()

    try:

        css_subqueries, static_info = await asyncio.gather(
            generate_css_subqueries(list_el_str), generate_static_info(relevant_text)
        )

        if css_subqueries is None or static_info is None:
            return "there was a problem parsing a response from the LLM!"

        for k, v in css_subqueries.items():
            if isinstance(v, str) and v.startswith(list_el.tag):
                v.strip(list_el.tag)
                v.strip(" > ")
                css_subqueries[k] = v

        return RssData(
            homepage=url,
            channel_title=static_info["channel_title"],
            channel_description=static_info["channel_description"],
            item_title=f"{base_query} {css_subqueries["item_title"]}",
            item_link=f"{base_query} {css_subqueries["item_link"]}",
            item_description=(
                f"{base_query} {css_subqueries["item_description"]}"
                if css_subqueries["item_description"] is not None
                else None
            ),
            item_pubDate=(
                f"{base_query} {css_subqueries["item_pubDate"]}"
                if css_subqueries["item_pubDate"] is not None
                else None
            ),
        )

    except openai.APIConnectionError as e:
        return f"The LLM server could not be reached: {e.__cause__}"
    except openai.RateLimitError:
        return "LLM rate limit reached!"
    except openai.APIStatusError as e:
        return f"The LLM server could not be reached: {e.response}"
    except Exception as e:
        print(e)
        return "Something went wrong!"
