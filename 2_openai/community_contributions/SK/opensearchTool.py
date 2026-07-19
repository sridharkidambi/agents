import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from agents import Agent, WebSearchTool, trace, Runner, function_tool
from agents.model_settings import ModelSettings
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import asyncio
from IPython.display import display, Markdown
from messenger import send_email, push
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

USE_EMAIL = True
# writer_agent=None
# email_agent=None
# planner_agent=None
# search_agent=None

class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")


class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")
    markdown_report: str = Field(description="The final report")
    follow_up_questions: list[str] = Field(description="Suggested topics to research further")


@function_tool
def send_email_tool(subject: str, text_body: str, html_body: str) -> str:
    """
    Send out an email with the given subject and body to all sales prospects
    
    Args:
        subject: The subject of the email
        text_body: The body of the email as plain text
        html_body: The HTML body of the email
    """
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("sridharhere@gmail.com")  # Change to your verified sender
    to_email = To("sridharkidambi@zohomail.com")  # Change to your recipient
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}

async def run_searches(query: str, planner_agent: Agent, search_agent: Agent):
    print("Planning searches...")
    result = await Runner.run(planner_agent, f"Query: {query}")
    searches = result.final_output.searches
    print(f"Will perform {len(searches)} searches")
    tasks = [do_search(item, search_agent) for item in searches]
    results = await asyncio.gather(*tasks)
    print("Finished searching")
    return results


async def do_search(item: WebSearchItem, search_agent: Agent):
    input_message = f"Search term: {item.query}\nReason for searching: {item.reason}"
    result = await Runner.run(search_agent, input_message)
    return result.final_output

async def write_report(query: str, search_results: list[str], writer_agent: Agent):
    print("Thinking about report...")
    input_message = f"Original query: {query}\nSummarized search results: {search_results}"
    result = await Runner.run(writer_agent, input_message)
    print("Finished writing report")
    return result.final_output

async def send_report_email(report: ReportData, email_agent: Agent):
    print("Writing email...")
    result = await Runner.run(email_agent, report.markdown_report)
    print("Email sent")
    return result.final_output

async def main():
    print("Starting the OpenSearch Tool Agent...")
    load_dotenv()
    MODEL_NAME = "gpt-4o-mini"
    HOW_MANY_SEARCHES = 5

    # SEARCH AGENT
    search_agent = Agent(
        name="Search Agent",
        instructions="""
    You are a research assistant. Given a search term, you search the web for that term and
    produce a concise summary of the results. The summary must be 2-3 paragraphs and less than 300 words.
    Capture the main points and be succinct. Reply only with the summary.
    """,
        tools=[WebSearchTool()],
        model=MODEL_NAME,
        model_settings=ModelSettings(tool_choice="required"),
    )

    # PLANNING AGENT
    planner_agent = Agent(
        name="Planner Agent",
        instructions=f"""
    You are a research assistant. Given a user query, come up with a set of web searches
    to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for.
    """,
        model=MODEL_NAME,
        output_type=WebSearchPlan,
    )

    # WRITER AGENT
    writer_agent = Agent(
        name="Writer Agent",
        instructions="""
    You are a senior researcher tasked with writing a cohesive report for a research query.
    You will be provided with the original query, and some research.
    Generate a comprehensive report based on the research and the query.
    The final output should be in markdown format, and it should be lengthy and detailed.
    Aim for 5-10 pages of content, at least 1000 words.
    """,
        model=MODEL_NAME,
        output_type=ReportData,
    )

    # EMAIL AGENT
    email_agent = Agent(
        name="Email Agent",
        instructions="""
    You are provided with a detailed report. Use your tool to send an email, converting the report into
    a clean, well presented HTML email with an appropriate subject line.
    """,
        tools=[send_email_tool],
        model=MODEL_NAME,
    )

    query = "Most popular AI Agent frameworks in 2026"

    with trace("Research trace"):
        print("Starting research...")
        search_results = await run_searches(query, planner_agent, search_agent)
        report = await write_report(query, search_results, writer_agent)
        await send_report_email(report, email_agent)
        display(Markdown(report.markdown_report))
        # print(json.dumps({"short_summary": report.short_summary, "follow_up_questions": report.follow_up_questions}, indent=2))
        print("Hooray!")








if __name__ == '__main__':
    asyncio.run(main())