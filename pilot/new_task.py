from termcolor import colored
from helpers.AgentConvo import AgentConvo
from helpers.Project import Project
from database.database import delete_subsequent_steps, get_development_step_from_hash_id, save_development_step
from helpers.Agent import Agent
from const.function_calls import IMPLEMENT_TASK
from utils.llm_connection import create_gpt_chat_completion, get_prompt
from utils.utils import array_of_objects_to_string
from utils.repo_api import get_repo_json, get_local_json, GET_REPO_FILES
class AgentConvo:
    def __init__(self, agent,system_message):
        self.agent = agent
        # self.messages = [{"role":"system","content":"You are an AI assistant that helps people reading code."}]
        self.messages = [{"role":"system","content":system_message}]
    #copy the postprocess_response from AgentConvo.py
    def remove_last_x_messages(self, x):
        # print("remove_last_x_messages")
        # return
        self.messages = self.messages[:-x]
    def postprocess_response(self, response, function_calls):
        # print("postprocess_response")
        # return
        if function_calls is not None and 'function_calls' in function_calls:
            if 'to_message' in function_calls:
                return function_calls['to_message'](response)
            elif 'to_json' in function_calls:
                return function_calls['to_json'](response)
            elif 'to_json_array' in function_calls:
                return function_calls['to_json_array'](response)
            else:
                return response
        else:
            if type(response) == tuple:
                return response[0]
            else:
                return response
    # copy construct_and_add_message_from_prompt from AgentConvo.py
    def construct_and_add_message_from_prompt(self, prompt_path, prompt_data):
        # print("construct_and_add_message_from_prompt")
        # return
        if prompt_path is None:
            prompt_path = self.agent.get_prompt_path()
        if prompt_data is None:
            prompt_data = self.agent.get_prompt_data()
        prompt = get_prompt(prompt_path, prompt_data)
        self.messages.append({"role": self.agent.role, "content": prompt})
        # self.log_message(prompt)

    def send_message(self, prompt_path=None, prompt_data=None, function_calls=None):
        # print("send_message to openai")
        # return
        # craft message
        self.construct_and_add_message_from_prompt(prompt_path, prompt_data)

        if function_calls is not None and 'function_calls' in function_calls:
            self.messages[-1]['content'] += '\nMAKE SURE THAT YOU RESPOND WITH A CORRECT JSON FORMAT!!!'
        response = create_gpt_chat_completion(self.messages, None, function_calls=function_calls)

        # TODO handle errors from OpenAI
        if response == {}:
            raise Exception("OpenAI API error happened.")

        response = self.postprocess_response(response, function_calls)

        # TODO remove this once the database is set up properly
        message_content = response[0] if type(response) == tuple else response
        if isinstance(message_content, list):
            if 'to_message' in function_calls:
                string_response = function_calls['to_message'](message_content)
            elif len(message_content) > 0 and isinstance(message_content[0], dict):
                string_response = [
                    f'#{i}\n' + array_of_objects_to_string(d)
                    for i, d in enumerate(message_content)
                ]
            else:
                string_response = ['- ' + r for r in message_content]

            message_content = '\n'.join(string_response)
        # TODO END

        # TODO we need to specify the response when there is a function called
        # TODO maybe we can have a specific function that creates the GPT response from the function call
        self.messages.append({"role": "assistant", "content": message_content})
        # self.log_message(message_content)

        return response
    
from helpers.agents.Developer import Developer
class Project:
    def __init__(self, args):
        self.args = args

# Create Project
project = Project({})

# Create Agent with correct role  
# agent = Agent('user', project)
# agent = Developer('user', project)
# convo = AgentConvo(agent,"You are an AI assistant that helps people reading code.")

# Load the new_task.prompt template
new_task_prompt = """
You will be provided with a reference project delimited by triple quotes. Your task is to use the reference project to write code for the new requirement: "{requirements}." \n\nEnsure that you don't extract small snippets that are missing important context.

Make sure that you give all the code, including lines with no changes of code from the reference project, and make sure there are no comments for just a description of the function. No "pseudo-code".

Try to code with a sophisticated thought of both timing and error handling.
```
reference project
```
"""
# creating a embedding for the reference project or current project or long conversation history
new_task_prompt = """ 
You will be provided with a reference project delimited by triple quotes. Your task is to use the reference project to answer the question: "{{questions}}." \n\nEnsure that you don't extract small snippets that are missing important context. 
```
{{reference_project}}
```
"""
questions = """
- how it save the snapshot of files
- how many pormpts are used in project, list in order of calling like in what step?
- how to get the prompt for a specific step?
"""
# Load the reference project
# url get from command line input
url = None
import os
import questionary
import json
# Import necessary modules (assuming they are imported in your original code)
# import json
# import questionary
import json
import questionary
from questionary import Choice


# check if skip following code

# Initialize buffer to store previous choices and outputs
buffer = {} 
reference_project = None

try:
    # Check buffer for previous source choice
    source_choice = buffer.get('source_choice') or questionary.select(
        "Choose the source of the reference project:",
        choices=[
            Choice("URL"),
            Choice("Local JSON file"),
            Choice("Local path via get_local_json()")
        ]
    ).ask()
    
    # Save to buffer
    buffer['source_choice'] = source_choice

    if source_choice == "URL":
        # Check buffer for previous URL
        url = questionary.text("Please enter the URL of the reference project (omit .git if present):").ask()
        
        # Remind user to drop .git from the URL if present
        if url and url.endswith(".git"):
            questionary.print("Note: Please omit the .git from the URL.")
            url = url[:-4]
        # Check if the user has entered a value for the URL
        if not url:
            url = buffer.get('url')
        # Save to buffer to a file
        buffer['url'] = url

        
        reference_project = get_repo_json(url)

    elif source_choice == "Local JSON file":
        with open('schema.json') as f:
            reference_project = json.load(f)

    elif source_choice == "Local path via get_local_json()":
        reference_project = get_local_json()

except KeyboardInterrupt:
    print("\nOperation cancelled by user.")



def save_prompt_to_file(prompt_path, new_task_prompt):
    # Save the new task prompt to a file
    with open(prompt_path, "w") as f:
        f.write(new_task_prompt)
    f.close()

# Save the new task prompt to a file
prompt_path = "prompts/new_task.prompt"
save_prompt_to_file(prompt_path, new_task_prompt)
prompt_path = "new_task.prompt"

# Build the prompt data
prompt_data = {
  "questions": questions,
  "reference_project": reference_project
}

print("prompt_data",prompt_data)
# if(questionary.test("Press Enter to continue...").ask == None):
#     print("continue")
# else:
#     quit()
#########################################
print("dividing line ###############################")

codeToQuestion = """you are provided the files structure of a project ```{{project_files}}```, pick one as a start point, make a query of content by the file path. after getting the content, you can use the content to answer the question: {{questions}}. \n\nEnsure that you don't extract small snippets that are missing important context. if content no include any useful info or  not enough context, find next possible file from the files structure. if it include useful info but not enough for anwsering the questions, Step by step psuedocode overview of major codepaths, full overview and walkthrough including major dependencies and imports, with high level brief summary of how they are used within the file major public interfaces, and how other classes might use them\n\nnote where this classes is used within the codebase, as of <today's date> and a list of related files"""

ProjectToDescrption = """you are provided the files structure of project ```{{project_files}}```, pick one as a start point, make a query of content by the file path. after getting the content, First think step-by-step then describe the file, including: Cool codename based on what it does, example network manger ->skynet Brief 2-3 sentence list summary\nStep by step psuedocode overview of major codepaths\n\na full overview and walkthrough including major dependencies and imports, with high level brief summary of how they are used within the file major public interfaces, and how other classes might use them\n\nnote where this classes is used within the codebase, as of <today's date> and a list of related files\n\n and next follow the above the dependencies logic find another file to query and repeat above steps. After All content should be written out in great detail, using markdown and styled like a fancy README.md\n\nFinally include instructions and tips for future LLM ai assistants who will read this."""

codeToImplementTask = "Ok, now, take your previous message and convert it to multi parts. which includes app_summary and user_stories and technologies"
#############
project = Project({})
# Create Agent with correct role  
agent = Agent('user', project)

system_message = "You are an AI assistant that helps people anwser quesions or finsih task based on a codebase.because the context limit, you do not get all the info at time.You get piece of content may  or may not related to the question or task you need to anwser or finish. Ensure that you don't extract small snippets that are missing important context, get enough content before you answer the question"
system_message_improved = """
You are an GitHub Project Reading helper, designed to asssit in comprehending and navigating Github Project. 
**Capabilities**
- Answering general questions about the project's architecture, purpose, and components.
- Guiding to relevant files or directories for specific tasks or functionalities.
- Providing summaries or explanations of specific sections of code.
**Limitations**
- due to limitations, you can't review the entire project at once, you can only review one file at a time.
- once you start a review, you can't stop until you finish the review of all the files you query. you need to raise questions to complete understanding of user request before you start.
- once you start the review, you the one to desice what to do next, you can't get the next step from user or ask user to provide the file path or any other info you need to continue the review.
"""
system_message_examples = """
You are an AI programming assistant tasked with writing a meaningful commit message by summarizing code changes.
- Follow the user's instructions carefully & to the letter!
- Don't repeat yourself or make anything up!
- Minimize any other prose
"""
how_to_use = """
📌 How to Use:
Project Overview: Start by briefly describing the project you're interested in. Include its purpose, language(s) used, and any specific areas you're struggling with.
user story: how to interact with the project

Targeted Questions: Ask focused questions about what you wish to understand. For example: "What does the function xyz in file.py do?" or "How is the database schema organized?"
Follow-up: Based on my responses, you can ask further questions or request additional explanations on specific topics.
follow-up question propose?
📌 IMPORTANT: Please refrain from sharing sensitive or confidential information as I am not designed to store or protect such data."""


rules = []
# rules.append("") # who do you act
# rules.append("You always think step by step and ask detailed questions to completely understand what user want to do.")
# rules.append("Give detail specifications for the next actions")
rules.append("Any Instruction you get which labeled as **IMPORTANT**, you follow strictly.")
# system_message.append(rules)
convo = AgentConvo(agent,system_message_improved + '\n\n'.join(rules))

codeToDescrption = """you are provided the files structure of a project```{{project_files}}```, pick one as a start point, make a query of content by the file path. """
codeToDescrption = """You are provided with the file structure of a project, represented as 
{{project_files}}
Before proceeding, seek clarification on any ambiguities in the question:
```
{{questions}}
```
 Ask detailed questions to understand fully what the user wants to know. Once clarified, choose one file that seems relevant to the question or information you seek. Then, make a query for the content of that specific file using its path.
"""
codeToDescrption = """
{% if clarifications and clarifications|length > 1 %}
You are provided with the file structure of a project in previous message.
{% else %}
You are provided with the file structure of a project, represented as ```{{project_files}}```.
{% endif %}
Step 1: Before proceeding with file exploration, seek clarification on any ambiguities : 
```{{questions}}```
Ask detailed questions to fully understand what the user wants to know.
Step 2:
```
Here is the list of clarifications: 
{% if clarifications and clarifications|length > 1 %}
    {% for clarification in clarifications %}
    {{clarification}}
    {% endfor %}

```
repeat Step 1 until the question is fully understood.
{% endif %}
Step 3: Once the question is clarified after , choose one file that seems relevant to the clarified question or information you seek. Then, make a query for the content of that specific file using its path.
***IMPORTANT***: Steps 1 and 2 should be iteratively executed until the question is completely clear. Only then proceed to Step 3."""


codeToDescrptionCont = "here is the content of the requested file which delimited by triple quotes ```{{file_content}}``` \
after getting the content: <<{{questions}}>> or still not ready to answer the question,query the next file to get more info. and before go to next file,if content include useful info but not enough for anwsering the questions, here is what need to extract and save as a snapshot of file content:Step by step psuedocode overview of major codepaths, full overview and walkthrough including major dependencies and imports, with high level brief summary of how they are used within the file major public interfaces, and how other classes might use them\n\nnote where this classes is used within the codebase \n\n***IMPLEMENT*** get enough content before you answer the question"

codeToDescrptionCont = """Upon receiving the content of the requested file:
```{{file_content}}```
analyze it to address the question:
```
{{questions}}
```
If the content includes useful information but isn't sufficient for answering the question, perform the following:
- Provide a full overview and walkthrough, including major dependencies and imports, and summarize their usage within the file.
- Note the major public interfaces and describe how other classes might use them.
- Mark where these classes are used within the codebase.

***IMPORTANT***: If the content still isn't enough to answer the question, continue to query the next relevant file for more information until you gather enough data to provide a well-informed answer.
"""

# if you need more content, you contine to query next possible file related to question or task: {{file_path}} \
# before go to next step, where this classes is used within the codebase, as of <today's date> and a list of related files\n\n and next follow the above the dependencies logic find another file to query and repeat above steps. \
# **SUMMARY** After All content should be written out in great detail, using markdown and styled like a fancy README.md\n\nFinally include instructions and tips for future LLM ai assistants who will read this. "

STEP_NEXT = {
    'definitions': [
        {
            'name': 'next_or_answer',
            'description': 'continue to query next possible file related to question or task or get all the info and can answer the question',
            'parameters': {
                'type': 'object',
                'properties': {
                    'type': {
                        'type': 'string',
                        'enum': ['next', 'answer'],
                        'description': 'continue to query next possible file related to question or get all the info and can answer the question, must be one of next or answer'
                    },
                    'next':{
                        'type': 'object',
                        'description': 'next possible file related to question or task, collect the content of file and save as a snapshot',
                        'properties': {
                            'file_path': {
                                'type': 'string',
                                'description': 'next possible file related to question or task'
                            },
                            'snapshot': {
                                'type': 'object',
                                'description': 'current file content include useful info but not enough for anwsering the questions',
                                'properties': {
                                    'summary': {
                                        'type': 'string',
                                        'description': 'summary of the file content'
                                    },
                                    'content': {
                                        'type': 'array',
                                        'description': 'major public interfaces, and how other classes might use them',
                                        'items': {
                                            'type': 'object',
                                            'properties': {
                                                'symbol_name': {
                                                    'type': 'string',
                                                    'description': 'name of symbol'
                                                },
                                                'reference': {
                                                    'type': 'string',
                                                    'description': 'file path of references of symbol'
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'anwser': {
                        'type': 'object',
                        'description': 'anwser of question',
                        'properties': {
                            'text': {
                                'type': 'string',
                                'description': 'anwser of question'
                            },
                            'file_to_change': {
                                'type': 'array',
                                'description': 'give list of the file path of the files need to change',
                                'items': {
                                    'type': 'string',
                                    'description': 'file path of the file need to change'
                                }
                            }
                        },
                        'required': ['text', 'file_to_change']
                    },
                   
                },
                'required': ['type']
            }
        }
    ],
    'functions': {
        'next_or_answer': lambda type, next, answer: {
            'type': type,
            'next': next,
            'answer': answer
        }
    }
}
# Save the new task prompt to a file
prompt_path = "prompts/new_task.prompt"
save_prompt_to_file(prompt_path, codeToDescrption)
prompt_path = "new_task.prompt"

project_files = get_local_json("/mnt/d/GitHub/gpt-pilot/pilot",only_path=True)
if isinstance(project_files, list):
    project_files = '\n\n'.join(project_files)
elif isinstance(project_files, dict):
    project_files = '\n\n'.join([f"{k}\n{v}" for k,v in project_files.items()])

questions = "which prompt it used to generate followup questions for a product owner to generate users stories?"
questions = "how to get the prompt for a specific step?"
questions = "how to debug the project"
questions = "update the code to use the Azure API instead of the OPENAI API"
print(questionary.print(f"questions: {questions}"))

task_description = convo.send_message(prompt_path, {
    'project_files': project_files,
        'questions': questions,
        'clarifications': [],
    }, GET_REPO_FILES)
# print(convo.messages[-2])
print(convo.messages[-1])  
while convo.messages[-1]['content']['function_calls']['name'] == "questions_clarification":
    # ret = questionary.print(f"ask clarifying questions: {convo.messages[-1]['content']['function_calls']['arguments']['questions']}")
    ret = []
    for i in convo.messages[-1]['content']['function_calls']['arguments']['clarifications']:
        ret.append(questionary.text(f"{i}").ask())
    print(ret)
    convo.remove_last_x_messages(1)
    task_description = convo.send_message(prompt_path, {
        'project_files': project_files,
        'questions': questions,
        'clarifications': ret,
        }, GET_REPO_FILES)
# data = json.loads(task_description)
function_name = task_description['function_calls']['name']
arguments = task_description['function_calls']['arguments']
print("next possible file related to question or task",arguments)
ret = GET_REPO_FILES['functions'][function_name](**arguments)
# print(ret)

# Save the new task prompt to a file
prompt_path = "prompts/new_task.prompt"
save_prompt_to_file(prompt_path, codeToDescrptionCont)
prompt_path = "new_task.prompt"

#send back llm
convo.remove_last_x_messages(1)   
convo.send_message(prompt_path, {
    "file_content": ret,
    "questions": questions,
}, STEP_NEXT)
# print(convo.messages[-2])
print(convo.messages[-1])
while convo.messages[-1]['content']['function_calls']['arguments']['type'] == 'next':
    arguments = convo.messages[-1]['content']['function_calls']['arguments']['next']['file_path']
    ret = GET_REPO_FILES['functions']['get_file_content'](arguments)
    convo.remove_last_x_messages(1)   
    convo.send_message(prompt_path, {
        "file_content": ret,
        "questions": questions,
    }, STEP_NEXT)
    # print(convo.messages[-2])
    print(convo.messages[-1])

# task_steps = convo.send_message('development/parse_task.prompt', {}, IMPLEMENT_TASK)
# convo.remove_last_x_messages(2)        
# task_description = convo.send_message('development/task/breakdown.prompt', {
#             "name": self.project.args['name'],
#             "app_summary": self.project.project_description,
#             "clarification": [],
#             "user_stories": self.project.user_stories,
#             # "user_tasks": self.project.user_tasks,
#             "technologies": self.project.architecture,
#             "array_of_objects_to_string": array_of_objects_to_string,
#             "directory_tree": self.project.get_directory_tree(True),
#             "current_task_index": i,
#             "development_tasks": self.project.development_plan,
#             "files": self.project.get_all_coded_files(),
#         })

# task_steps = convo.send_message('development/parse_task.prompt', {}, IMPLEMENT_TASK)
# convo.remove_last_x_messages(2)
# # ...

