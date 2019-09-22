import argparse
from collections import defaultdict
import os
import importlib
import inspect

import yaml


def normalize_docstring(string):
    if string is None:
        return ""
    return string.replace("    ", "")


def get_relative_name(fully_qualified_name):
    if "." in fully_qualified_name:
        return fully_qualified_name.split(".")[-1]
    else:
        return fully_qualified_name


def load_index_md():
    with open(os.path.join(os.path.dirname(__file__), "index.md")) as index:
        return index.read()


def load_pydocmd_yml():
    with open(os.path.join(os.path.dirname(__file__), "pydocmd.yml")) as file:
        return yaml.safe_load(file)["generate"][0]["docs.md"]


def get_module(module_def):
    if isinstance(module_def, str):
        module_name = module_def
        definitions = []
        module = importlib.import_module(module_def)
    else:
        for module_name, definitions in module_def.items():
            module = importlib.import_module(module_name)
            break
    return module_name, module, definitions


def get_exception_doc_data(exception):
    return {"name": exception.__name__, "doc": normalize_docstring(exception.__doc__)}


def get_function_doc_data(function):
    return {
        "signature": function.__name__ + str(inspect.signature(function)),
        "doc": normalize_docstring(function.__doc__),
    }


def get_method_doc_data(method, method_name):
    try:
        signature = str(inspect.signature(method))
    except TypeError:
        signature = "(self)"

    return {
        "signature": method_name + signature,
        "doc": normalize_docstring(method.__doc__),
    }


def get_class_doc_data(class_, methods_docs):
    return {
        "name": class_.__name__,
        "doc": normalize_docstring(class_.__doc__),
        "methods": methods_docs,
    }


def get_module_doc_data(module_name, module, docs):
    return {
        "name": module_name,
        "doc": normalize_docstring(module.__doc__),
        "functions": docs["function"],
        "classes": docs["class"],
        "exceptions": docs["exception"],
    }


def get_function_or_exception_doc(module, definition):
    function_or_exception = getattr(module, get_relative_name(definition))
    if isinstance(function_or_exception, type):
        return "exception", get_exception_doc_data(function_or_exception)
    else:
        return "function", get_function_doc_data(function_or_exception)


def get_class_doc(module, definition):
    for class_name, methods in definition.items():
        class_ = getattr(module, get_relative_name(class_name))
        methods_docs = []
        for method_def in methods:
            method_name = get_relative_name(method_def)
            methods_docs.append(
                get_method_doc_data(getattr(class_, method_name), method_name)
            )
        return "class", get_class_doc_data(class_, methods_docs)


def get_doc(module, definition):
    if isinstance(definition, str):
        return get_function_or_exception_doc(module, definition)
    else:
        return get_class_doc(module, definition)


def get_module_docs(module, definitions):
    docs = defaultdict(list)
    for definition in definitions:
        doc_type, doc = get_doc(module, definition)
        docs[doc_type].append(doc)
    return docs


def get_doc_data(readme_top, modules):
    doc_data = {"index": readme_top, "modules": []}
    for module_def in modules:
        module_name, module, definitions = get_module(module_def)
        doc = get_module_doc_data(
            module_name, module, get_module_docs(module, definitions)
        )
        doc_data["modules"].append(doc)
    return doc_data


def collect_doc_data():
    return get_doc_data(load_index_md(), load_pydocmd_yml())


def assemble_class_docs(class_):
    method_docs = "\n\n".join(
        "##" + assemble_function_docs(method) for method in class_["methods"]
    )

    return """#### `{name}`

{doc}

##### Methods

{method_docs}

---

""".format(
        name=class_["name"], doc=class_["doc"], method_docs=method_docs
    )


def assemble_function_docs(function):
    return """#### `{signature}`

{doc}
""".format(
        signature=function["signature"], doc=function["doc"]
    )


def assemble_exception_docs(exception):
    return """#### `{name}`

{doc}
""".format(
        name=exception["name"], doc=exception["doc"]
    )


def assemble_module_docs(module):
    class_docs = "\n\n".join(
        assemble_class_docs(class_) for class_ in module["classes"]
    )
    function_docs = "\n\n".join(
        assemble_function_docs(function) for function in module["functions"]
    )
    exception_docs = "\n\n".join(
        assemble_exception_docs(exception) for exception in module["exceptions"]
    )
    doc = """## `{name}`

{module_doc}
""".format(
        name=module["name"], module_doc=module["doc"]
    )

    if class_docs:
        doc += """### Classes

{class_docs}
""".format(
            class_docs=class_docs
        )

    if function_docs:
        doc += """### Functions

{function_docs}
""".format(
            function_docs=function_docs
        )

    if exception_docs:
        doc += """### Exceptions

{exception_docs}
""".format(
            exception_docs=exception_docs
        )

    doc += """

---

"""

    return doc


def assemble_table_of_contents(data):
    output = []
    for module in data["modules"]:
        output.append(
            "* <a href='#{}'>`{}`</a>".format(
                module["name"].replace(".", ""), module["name"]
            )
        )
        for class_ in module["classes"]:
            output.append(
                "    * Class <a href='#{}'>`{}`</a>".format(
                    class_["name"].replace(".", ""), class_["name"]
                )
            )
            for method in class_["methods"]:
                output.append(
                    "        * Method `{}.{}`".format(
                        class_["name"], method["signature"]
                    )
                )
        for function in module["functions"]:
            output.append("    * Function `{}`".format(function["signature"]))
        for exception in module["exceptions"]:
            output.append("    * Exception `{}`".format(exception["name"]))
    return "\n".join(output)


def assemble_docs(data):
    module_docs = "\n\n".join(
        assemble_module_docs(module) for module in data["modules"]
    )
    table_of_contents = assemble_table_of_contents(data)
    return """{index}
---

# Documentation

## Table of contents
{table_of_contents}

{module_docs}
""".format(
        index=data["index"],
        table_of_contents=table_of_contents,
        module_docs=module_docs,
    )


def generate_doc(filename):
    data = collect_doc_data()
    readme_string = assemble_docs(data)

    if filename:
        with open(filename, "w") as readme:
            readme.write(readme_string)
    else:
        print(readme_string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o, --output",
        dest="output",
        help="Where to store the output. If not provided, documentation is printed",
        default=None,
    )
    args = parser.parse_args()

    generate_doc(args.output)
