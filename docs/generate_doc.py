import os
import importlib
import inspect

import yaml


def normalize_docstring(string):
    if string is None:
        return ""
    return string.replace("    ", "")


def collect_doc_data():
    with open(os.path.join(os.path.dirname(__file__), "index.md")) as index:
        readme_top = index.read()

    with open(os.path.join(os.path.dirname(__file__), "pydocmd.yml")) as file:
        data = yaml.safe_load(file)

    modules = data["generate"][0]["docs.md"]
    doc_data = {"index": readme_top, "modules": []}
    for module_def in modules:
        if isinstance(module_def, str):
            module_name = module_def
            definitions = []
            module = importlib.import_module(module_def)
        else:
            for module_name, definitions in module_def.items():
                module = importlib.import_module(module_name)
                break

        function_docs = []
        class_docs = []
        exception_docs = []

        for definition in definitions:
            if isinstance(definition, str):
                function = getattr(module, definition.split(".")[-1])
                if isinstance(function, type):
                    exception_docs.append(
                        {
                            "name": function.__name__,
                            "doc": normalize_docstring(function.__doc__),
                        }
                    )
                else:
                    function_docs.append(
                        {
                            "signature": function.__name__
                            + str(inspect.signature(function)),
                            "doc": normalize_docstring(function.__doc__),
                        }
                    )
            else:
                for class_name, methods in definition.items():
                    class_ = getattr(module, class_name.split(".")[-1])
                    methods_docs = []
                    for method_def in methods:
                        method_name = method_def.split(".")[-1]
                        method = getattr(class_, method_name)
                        try:
                            signature = str(inspect.signature(method))
                        except TypeError:
                            signature = "(self)"
                        methods_docs.append(
                            {
                                "signature": method_name + signature,
                                "doc": normalize_docstring(method.__doc__),
                            }
                        )
                    class_docs.append(
                        {
                            "name": class_.__name__,
                            "doc": normalize_docstring(class_.__doc__),
                            "methods": methods_docs,
                        }
                    )

        doc_data["modules"].append(
            {
                "name": module_name,
                "doc": normalize_docstring(module.__doc__),
                "functions": function_docs,
                "classes": class_docs,
                "exceptions": exception_docs,
            }
        )
    return doc_data


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


def generate_doc():
    data = collect_doc_data()
    readme_string = assemble_docs(data)

    with open(
        os.path.join(os.path.dirname(__file__), "..", "readme.md"), "w"
    ) as readme:
        readme.write(readme_string)


if __name__ == "__main__":
    generate_doc()
