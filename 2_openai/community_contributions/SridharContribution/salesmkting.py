"""
Sales and Marketing Email Module

Dependencies (install via: pip install -r requirements.txt):
- python-dotenv
- sendgrid
"""

from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv
from agents import Agent, GuardrailFunctionOutput, OpenAIChatCompletionsModel, Runner, input_guardrail, output_guardrail, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import asyncio


load_dotenv(override=True)


def send_test_email(from_address: str, to_address: str) -> int:
    """Send a simple HTML test email via SendGrid. Returns HTTP status code."""
    api_key = os.environ.get('SENDGRID_API_KEY')
    if not api_key:
        raise RuntimeError('SENDGRID_API_KEY not set in environment')

    sg = sendgrid.SendGridAPIClient(api_key=api_key)
    from_email = Email(from_address)
    to_email = To(to_address)
    content = Content("text/html", _HTML_BODY)
    mail = Mail(from_email, to_email, "Chai Time at the Center!", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    return response.status_code


_HTML_BODY = """
<html>
  <body style="font-family: Arial, sans-serif; background-color:#f4f4f4; padding:20px;">
    <div style="max-width:600px; margin:auto; background:#ffffff; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.1); overflow:hidden;">
      <div style="background:#1a73e8; color:#ffffff; padding:24px; text-align:center;">
        <h1 style="margin:0; font-size:28px;">Chai Time at the Center!</h1>
      </div>
      <div style="padding:24px; color:#333333; line-height:1.6;">
        <p>Hi there,</p>
        <p>Let's meet up with Rohit, Vidyadhar, Avinash, Ram, and Ramalingam near the center for some chai!</p>
        <p style="text-align:center;">
          <a href="https://maps.google.com" style="display:inline-block; padding:12px 22px; background:#1a73e8; color:#ffffff; text-decoration:none; border-radius:6px;">Find the Location</a>
        </p>
        <p>Looking forward to catching up over chai in Chennai,<br/>See you soon!</p>
      </div>
    </div>
  </body>
</html>
"""

@function_tool
def send_email(body: str):
    """ Send out an email with the given body to all sales prospects """
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("sridharhere@gmail.com")  # Change to your verified sender
    to_email = To("sridharkidambi@zohomail.com")  # Change to your recipient
    content = Content("text/html", body)
    mail = Mail(from_email, to_email, "Sales email", content).get()
    sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}

class NameCOutputOutput(BaseModel):
    is_Professional: bool= Field(description="Indicates if the content is professional.")

# @output_guardrail
# async def guardrail_against_output(ctx, agent, message):
#     result = await Runner.run(cowboy_agent, message, context=ctx.context)
#     return GuardrailFunctionOutput(output_info={"review": "output validated"}, tripwire_triggered=False)


async def main():
    
    # from_addr = os.environ.get('EMAIL_FROM', 'sridharhere@gmail.com')
    # to_addr = os.environ.get('EMAIL_TO', 'k.avinashca@gmail.com')
    # status = send_test_email(from_addr, to_addr)
    # print('Email send status:', status)

    instructions1 = "You are a Enterprise Agentic Architect in Sridhar Kdiambi Solutions , \
    a company that provides a agentic solutions and automation in  compliance and preparing for audits, powered by AI. \
    "

    instructions2 = "You are a Enterprise Agentic Architect in Sridhar Kdiambi Solutions , \
    a company that provides a agentic solutions and automation in  compliance and preparing for audits, powered by AI. \
    "

    deepseek_api_key = os.environ.get('DEEPSEEK_API_KEY')
    DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

    deepseek_client = AsyncOpenAI(base_url=DEEPSEEK_BASE_URL, api_key=deepseek_api_key)
    deepseek_model = OpenAIChatCompletionsModel(model="deepseek-chat", openai_client=deepseek_client)



    print(NameCOutputOutput.model_json_schema)

    instructions3 = "speak like a cowboy  and in a non professional tone"

    checked_agent = Agent(
      
        name="Checked Agent",
        instructions= instructions3,
        model="gpt-4o-mini",
        output_type=NameCOutputOutput 
    )
    result = await Runner.run(checked_agent, "Write a content for linkedin and other social media platforms. It should be engaging")


    instructions4 = "speak like a cowboy  and in a non professional tone"
    cowboy_agent = Agent(
            name="Cowboy Agentic AI Architect Sales Agent",
            instructions=instructions4,
            model="gpt-4o-mini",
            output_type=NameCOutputOutput
        )
    result = await Runner.run(cowboy_agent, "Write a content for linkedin and other social media platforms. It should be engaging  and detailed with sections ine eplaining the various gaurdrails,data leakage,prompt injection and governance.It should have a image to illustrate the concepts and also how to overcome these in enterprise world.Number of workds should not cross 400 words and should be in a professional tone and human generated content. It should be in a blog format with sections and sub-sections and also have a conclusion at the end.Create html page with image")
    print("Cowboy Agent Result:", result.final_output)
    EnterpriseArchitect_agent1 = Agent(
                name="Enterprise Agentic AI Architect Sales Agent",
                instructions=instructions1,
                model="gpt-4o-mini"
        )

    EnterpriseArchitect_agent2 = Agent(
            name="Enterprise Agentic AI Architect Sales Agent",
            instructions=instructions2,
            model=deepseek_model
    )
    # print(cowboy_agent)
    # print(EnterpriseArchitect_agent1)
    # print(EnterpriseArchitect_agent2)
    # print(send_email)

    description = "You are assigned to write a professional content, architecturing concepets for publishing in Linkedin and other social media platforms. It should be engaging  and detailed with sections ine eplaining the various gaurdrails,data leakage,prompt injection and governance.It should have a image to illustrate the concepts and also how to overcome these in enterprise world.Number of workds should not cross 400 words and should be in a professional tone and human generated content. It should be in a blog format with sections and sub-sections and also have a conclusion at the end.Create html page with image"

    tool1 = EnterpriseArchitect_agent1.as_tool(tool_name="EnterpriseArchitect_agent1", tool_description=description)
    tool2 = EnterpriseArchitect_agent2.as_tool(tool_name="EnterpriseArchitect_agent2", tool_description=description)

    tools = [tool1, tool2, send_email]



    instructions = """
    You are the head of Enterprise Architect leadership at Sridhar Kdiambi Solutions . Your goal is to find the single best linkedin content to be  email using the send_email tools.
    
    Follow these steps carefully:
    1. Generate Drafts: Use all two  EnterpriseArchitect_agent tools to generate two  different content for linkedIn to be emailed. Do not proceed until all two drafts are ready.
    
    2. Evaluate and Select: Review the drafts and choose the single best content for email using your judgment of which one is most effective.
    
    3. Use the send_email tool to send the best email (and only the best email) to the user.Also include a brief explanation of why you chose that email.and also include professional html formatting for the email body
    
    Crucial Rules:
    - You must use the EnterpriseArchitect agent1 tools to generate the drafts — do not write them yourself.
    - You must send ONE email using the send_email tool — never more than one.
    """


    EA_manager = Agent(name="EA Manager", instructions=instructions, tools=tools, model="gpt-4o-mini")

    message = "Send an  email addressed to 'Dear Sridhar Kidambi'"

    # with trace("EA manager"):
    #     result = await Runner.run(EA_manager, message)





# @input_guardrail
# async def guardrail_against_name(ctx, agent, message):
#     result = await Runner.run(guardrail_agent, message, context=ctx.context)
#     is_name_in_message = result.final_output.is_professional
#     return GuardrailFunctionOutput(output_info={"review": result.final_output},tripwire_triggered=is_name_in_message)

if __name__ == '__main__':
    asyncio.run(main())

    # https://platform.openai.com/logs/trace?trace_id=trace_ca895754d661403ab1470ed3a4c88e5e

