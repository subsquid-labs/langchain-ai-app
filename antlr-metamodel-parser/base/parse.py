import sys

from solidity_parser import parser


import json

from pathlib import Path
from pprint import pprint
import uuid

# from pprint import pprint


# Generate a unique ID for a metamodel component
def generate_id():
    return str(uuid.uuid4())


def assign_ids(data, parent_id=None, parent_type=None):
    # Generate a unique ID for the current component

    # Check for children in the component and recursively assign IDs
    if isinstance(data, str) == False:
        current_id = str(uuid.uuid4())
        # Add ID and parentComponentId to the component
        data["id"] = current_id

        data["parentId"] = parent_id
        current_type = data["type"]
        data["parentType"] = parent_type
        # state variables

        # function body
        if "body" in data:
            if "statements" in data["body"]:
                for child in data["body"]["statements"]:
                    if child["type"] == "ExpressionStatement":
                        assign_ids(child["expression"], current_id, current_type)
                        if child["expression"]["right"]:
                            assign_ids(
                                child["expression"]["right"], current_id, current_type
                            )
                        if child["expression"]["left"]:
                            assign_ids(
                                child["expression"]["left"], current_id, current_type
                            )
        # TODO
        if "returnParameters" in data:
            for child in data["returnParameters"]:
                assign_ids(child, current_id, current_type)
        # input parameters
        if "parameters" in data:
            for child in data["parameters"]["parameters"]:
                assign_ids(child, current_id, current_type)
        if "children" in data:
            for child in data["children"]:
                assign_ids(child, current_id, current_type)
        elif "subNodes" in data:
            for child in data["subNodes"]:
                assign_ids(child, current_id, current_type)

    return data


def convert_json(data, instances):
    for item in data:
        # handle state variables
        if item["type"] == "StateVariableDeclaration":
            instances[item["id"]] = {
                "id": item["id"],
                "toGenerate": True,
                "componentId": [],
                "attributes": {
                    "contractRef": item["parentId"],
                    "varLocation": [""],
                    "scope": [""],
                    "functionRef": [""],
                    "eventRef": [""],
                    "dataEntityRef": [""],
                    "elementRef": [""],
                    "modifierRef": [""],
                    "mappingRef": [""],
                    "operationRef": [""],
                },
            }
            variables = item["variables"]
            # handle simple variables
            if "name" in variables[0]["typeName"]:
                instances[item["id"]]["attributes"]["visibility"] = variables[0][
                    "visibility"
                ]
                pprint(variables[0])
                instances[item["id"]]["attributes"]["subtype"] = variables[0][
                    "typeName"
                ]["name"]
                if variables[0]["typeName"]["type"] == "ElementaryTypeName":
                    instances[item["id"]]["attributes"]["type"] = "simple"
            # TODO handle mappings
            ###

        ### handle functions
        if item["type"] == "FunctionDefinition":
            instances[item["id"]] = {
                "id": item["id"],
                "toGenerate": True,
                "componentId": ["FunctionCustom"],
                "attributes": {
                    "contractRef": [item["parentId"]],
                    "isCrossContract": ["false"],
                    "isPayable": ["false"],
                    "name": [item["name"]],
                    "visibility": [item["visibility"]],
                    "inputParams": [""],
                    "returnParam": [""],
                    "modifiers": [""],
                    "elementRef": [""],
                    "functionElements": [""],
                    "componentId": ["FunctionCustom"],
                },
            }
            # handle empty params
            if item["returnParameters"] == []:
                instances[item["id"]]["attributes"]["returnParam"] = [""]
            if item["parameters"] == []:
                instances[item["id"]]["attributes"]["inputParams"] = [""]
            # handle function elements
            statements = item["body"]["statements"]
            for statement in statements:
                if statement["type"] == "ExpressionStatement":
                    expression = statement["expression"]
                    id = generate_id()
                    functionElement = {
                        "id": id,
                        "toGenerate": "true",
                        "componentId": [""],
                        "attributes": {
                            "primaryScope": [""],
                            "operation": [""],
                            "name": [""],
                            "flowStep": ["1"],
                            "destinations": [""],
                            "functionRef": [instances[item["id"]]["id"]],
                            "elementRef": [""],
                            "componentId": [""],
                        },
                    }

                    if (
                        expression["type"] == "BinaryOperation"
                        and expression["operator"] == "="
                    ):
                        functionElement["attributes"]["componentId"] = [
                            "ElementDataEntityInstantiation"
                        ]
                        # TODO dataentities for operation
                        operationId = expression["id"]
                        operationAssign = {
                            "id": operationId,
                            "toGenerate": "true",
                            "componentId": ["OperationAssign"],
                            "attributes": {
                                "operator": ["="],
                                "term01": [expression["left"]["id"]],
                                "term02": [expression["right"]["id"]],
                                "flowStep": ["1"],
                                "destinations": [""],
                                "functionRef": [""],
                                "elementRef": [""],
                                "componentId": [""],
                            },
                        }
                        functionElement["attributes"]["operation"] = [operationId]
                        instances[operationId] = operationAssign

                    name = (
                        functionElement["id"][0]
                        + functionElement["attributes"]["componentId"][0]
                    )
                    functionElement["attributes"]["name"] = [name]
                    instances[functionElement["id"]] = functionElement

    return instances


def merge_lists(list1, list2):
    list3 = []
    for item in list1:
        list3.append(item)
    for item in list2:
        list3.append(item)
    return list3


# def getElementAssign():


def create_parsed_json():
    sourceUnit = parser.parse_file("../contract/cont.sol", loc=False)
    sourceUnit = assign_ids(sourceUnit)
    with open("../contract/data.json", "w", encoding="utf-8") as f:
        json.dump(sourceUnit, f, ensure_ascii=False, indent=4)
    instances = {}
    data = sourceUnit["children"][1]["subNodes"]
    result = convert_json(data, instances)
    with open("../contract/result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


def read_contract_json():
    file_path = "../contract/data.json"
    data = json.loads(Path(file_path).read_text())
    return data


def read_metamodel():
    file_path = "../contract/metamodel.json"
    metamodel = json.loads(Path(file_path).read_text())
    return metamodel


def parse_data(data):
    pprint(data["children"][1]["subNodes"])


if __name__ == "__main__":
    # asyncio.run(inspect_with_langchain(openai_key))
    create_parsed_json()
    contract = read_contract_json()
