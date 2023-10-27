"""PlaygroundsSubgraphConnectorToolSpec."""

from typing import Optional, Union
from langchain.agents import AgentExecutor


import openai
import logging
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from llama_index.agent import OpenAIAgent
import requests

from llama_index.bridge.langchain import FunctionMessage
from langchain.agents import initialize_agent, AgentType

from llama_hub.tools.graphql.base import GraphQLToolSpec
import json
from typing import Sequence

from llama_index.llms import OpenAI as OpenAI_LLM

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.memory import ChatMessageHistory

from llama_index.tools import BaseTool, FunctionTool
from langchain.tools import BaseTool, StructuredTool

import asyncio
import os

"""InspectorToolSpec."""


def introspect_schema() -> str:
    """
    Introspects the subgraph and summarizes its schema into textual categories.

    Returns:
        str: A textual summary of the introspected subgraph schema.
    """
    introspection_query = """
        query {
            __schema {
                types {
                    kind
                    name
                    description
                    enumValues {
                        name
                    }
                    fields {
                        name
                        args {
                            name
                        }
                        type {
                            kind
                            name
                            ofType {
                                name
                            }
                        }
                    }
                }
            }
        }
        """
    url = "https://squid.subsquid.io/swaps-squid/v/v1/graphql"

    response = requests.post(url, json={"query": introspection_query})
    # print(response.text)
    data = response.json()
    print(data["data"])
    if "data" in data:
        result = data["data"]
        processed_subgraph = _process_subgraph(result)
        print(subgraph_to_text(processed_subgraph))
        return subgraph_to_text(processed_subgraph)
    else:
        print("Error during introspection.")
        return "Error during introspection."


def _process_subgraph(result: dict) -> dict:
    """
    Processes the introspected subgraph schema into categories based on naming conventions.

    Args:
        result (dict): Introspected schema result from the GraphQL query.

    Returns:
        dict: A processed representation of the introspected schema, categorized into specific entity queries, list entity queries, and other entities.
    """
    processed_subgraph = {
        "specific_entity_queries": {},
        "list_entity_queries": {},
        "other_entities": {},
    }
    for type_ in result["__schema"]["types"]:
        if type_["name"].startswith("__"):
            continue  # Skip meta entities

        entity_name = type_["name"]
        fields, args_required = _get_fields(type_)
        if fields:
            # Determine category based on naming convention
            if entity_name.endswith("s") and not args_required:
                processed_subgraph["list_entity_queries"][entity_name] = fields
            elif not entity_name.endswith("s") and args_required:
                processed_subgraph["specific_entity_queries"][entity_name] = fields
            else:
                processed_subgraph["other_entities"][entity_name] = fields

    return processed_subgraph


def subgraph_to_text(subgraph: dict) -> str:
    """
    Converts a processed subgraph representation into a textual summary based on entity categories.

    Args:
        subgraph (dict): A processed representation of the introspected schema, categorized into specific entity queries, list entity queries, and other entities.

    Returns:
        str: A textual summary of the processed schema.
    """
    sections = [
        (
            "Specific Entity Queries (Requires Arguments)",
            "These queries target a singular entity and require specific arguments (like an ID) to fetch data.",
            """
            {
                entityName(id: "specific_id") {
                    fieldName1
                    fieldName2
                    ...
                }
            }
            """,
            subgraph["specific_entity_queries"],
        ),
        (
            "List Entity Queries (Optional Arguments)",
            "These queries fetch a list of entities. They don't strictly require arguments but often accept optional parameters for filtering, sorting, and pagination. ",
            
            """
            {
                entityNames(limit: 10, orderBy: "someField", orderDirection: "asc") {
                    fieldName1
                    fieldName2
                    ...
                }
            }
            """ "For limit the amount of results use limi argument like this. This example limits output to 10" """
            {
                entityNames(limit: 10) {
                    fieldName1
                    fieldName2
                    ...
                }
            }
            """,
            subgraph["list_entity_queries"],
        ),
        (
            "Other Entities",
            "These are additional entities that may not fit the conventional singular/plural querying pattern of subgraphs.",
            "",
            subgraph["other_entities"],
        ),
    ]

    result_lines = []
    for category, desc, example, entities in sections:
        result_lines.append(format_section(category, desc, example, entities))

    return "\n".join(result_lines)


def _get_fields(type_):
    """
    Extracts relevant fields and their details from a given type within the introspected schema.

    Args:
        type_ (dict): A type within the introspected schema.

    Returns:
        tuple: A tuple containing a list of relevant fields and a boolean indicating if arguments are required for the fields.
    """
    fields = []
    args_required = False
    for f in type_.get("fields") or []:
        if f["name"] != "__typename" and not (
            f["name"].endswith("_filter")
            or f["name"].endswith("_orderBy")
            or f["name"].islower()
        ):
            field_info = {"name": f["name"]}

            # Check for enum values
            if "enumValues" in f["type"] and f["type"]["enumValues"]:
                field_info["enumValues"] = [
                    enum_val["name"] for enum_val in f["type"]["enumValues"]
                ]

            fields.append(field_info)
            if f.get("args") and len(f["args"]) > 0:
                args_required = True
            if f.get("type") and f["type"].get("fields"):
                subfields, sub_args_required = _get_fields(f["type"])
                fields.extend(subfields)
                if sub_args_required:
                    args_required = True
    return fields, args_required


def format_section(
    category: str, description: str, example: str, entities: dict
) -> str:
    """
    Formats a given section of the subgraph introspection result into a readable string format.

    Args:
        category (str): The category name of the entities.
        description (str): A description explaining the category.
        example (str): A generic GraphQL query example related to the category.
        entities (dict): Dictionary containing entities and their fields related to the category.

    Returns:
        str: A formatted string representation of the provided section data.
    """
    section = [
        f"Category: {category}",
        f"Description: {description}",
        "Generic Example:",
        example,
        "\nDetailed Breakdown:",
    ]

    for entity, fields in entities.items():
        section.append(f"  Entity: {entity}")
        for field_info in fields:
            field_str = f"    - {field_info['name']}"
            if "enumValues" in field_info:
                field_str += f" (Enum values: {', '.join(field_info['enumValues'])})"
            section.append(field_str)
        section.append("")  # Add a blank line for separation

    section.append("")  # Add another blank line for separation between sections
    return "\n".join(section)


openai_key = "sk-OPENAI_API_KEY"


def graphql_request(
    query: str,
    variables: Optional[dict] = None,
    operation_name: Optional[str] = None,
) -> Union[dict, str]:
    """
    Make a GraphQL query.

    Args:
        query (str): The GraphQL query string to execute.
        variables (dict, optional): Variables for the GraphQL query. Default is None.
        operation_name (str, optional): Name of the operation, if multiple operations are present in the query. Default is None.

    Returns:
        dict: The response from the GraphQL server if successful.
        str: Error message if the request fails.
    """

    payload = {"query": query.strip()}

    if variables:
        payload["variables"] = variables

    if operation_name:
        payload["operationName"] = operation_name

    try:
        TIMEOUT_SECONDS = 300  # 5 mins timeout, the graph network can sometimes have unusually long response
        # response = requests.post(self.url, headers=self.headers, json=payload, timeout=TIMEOUT_SECONDS)
        url = "https://squid.subsquid.io/swaps-squid/v/v1/graphql"
        response = requests.post(url, json=payload)
        print(response.text)

        # Check if the request was successful
        response.raise_for_status()

        # Return the JSON response
        print(response.text)
        return response.json()

    except requests.RequestException as e:
        # Handle request errors
        return str(e)

    except requests.Timeout:
        return "Request timed out"

    except ValueError as e:
        # Handle JSON decoding errors
        return f"Error decoding JSON: {e}"


def sort_by_date(response: Union[dict, str])-> Union[dict, str]:
    """
    Sorts the response by timestamp or blockNumber. Timestamp is the same as date.

    Args:
        response (Union[dict, str]): The response from the GraphQL server.

    Returns:
        dict: The sorted response.
    """
    if isinstance(response, dict):
        if "data" in response:
            
            if "swaps" in response["data"]:
                print('yes1')
                if len(response["data"]["swaps"])>0 and "timestamp" in response["data"]["swaps"][0]:
                    print('yes')
                    response["data"]["swaps"].sort(key=lambda x: int(x["timestamp"]))
                elif "blockNumber" in response["data"]["swaps"]:
                    response["data"]["swaps"].sort(key=lambda x: x["blockNumber"])
                return response
            else:
                return "No swaps found"
        else:
            return "No data found"
    else:
        return response

tool1 = StructuredTool.from_function(graphql_request, description="Make a GraphQL query. Useful for when you need to fetch data. If you need to fetch a specific number of entities, use limit instead of first")
tool2 = StructuredTool.from_function(introspect_schema, description="Introspects the subgraph and summarizes its schema into textual categories.Useful for when you need to examine the schema of the API")
tool3 = StructuredTool.from_function(sort_by_date, description="Sorts the response by timestamp or blockNumber. Timestamp is the same as date. Useful for when you need to sort the response by date")
prompt = """query MyQuery {
  swaps(limit: 5, orderBy: id_ASC) {
    id
    amount1
    amount0
    blockNumber
  }
}
query and provide consice summary of the data. show only the summary"""
agent_kwargs = {
    "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
}
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)


def inspect_with_llama(prompt, openai_key):
    query_tool = FunctionTool.from_defaults(fn=graphql_request)
    introspect_tool = FunctionTool.from_defaults(fn=introspect_schema)
    openai.api_key = openai_key
    llm = OpenAI_LLM(model="gpt-4")

    agent = OpenAIAgent.from_tools([query_tool, introspect_tool], llm=llm, verbose=True)
    print(agent.chat(prompt))

my_tools = [tool1, tool2, tool3]    
async def inspect_with_langchain(input, openai_key):
    llm = ChatOpenAI(temperature=0, openai_api_key=openai_key)
    
    agent_chain = initialize_agent( my_tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True,agent_kwargs=agent_kwargs,
    memory=memory)
    
    hist_string = "Previous conversation: {chat_history} Current question: "
    prompt = hist_string+input

    response = await agent_chain.ainvoke({"input": prompt})
    


    print("_________RESPONSE_________")
    print(response['output'])
    return response['output']
