import importlib
import logging
import os
import re
import shlex

from collections.abc import Callable

from .http import HTTPResponse


ComponentCallbackType = Callable[[list[str], dict[str, str]], str]


def is_valid_python_module_name(p_name: str) -> bool:
    return re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", p_name) != None


class Component:
    def __init__(self):
        self.name: str = ""
        self.callback: ComponentCallbackType|None = None


class HTMLTemplateRenderer:
    def __init__(self) -> None:
        self.components: list[Component] = []


    def component(self, p_name: str) -> Callable:

        def definition_wrapper(p_decorated_function: Callable) -> Callable:

            def call_wrapper(*p_args, **p_kwargs) -> str:
                return p_decorated_function(*p_args, **p_kwargs)

            self.register_component(p_name, call_wrapper)

            return call_wrapper

        logging.info(f"Registered component `{p_name}`")

        return definition_wrapper

    
    def render(self, p_source: str, **p_kwargs: dict) -> str:
        rendered_source: str = p_source

        # NOTE(vanya): Replace all VARIABLE syntax with registered components until none are left
        while True:
            # NOTE(vanya): Match syntax
            regex_match = re.search(r"<!--\s*\$.*?-->", rendered_source, re.S)
            
            if regex_match == None:
                # NOTE(vanya): No syntax left to replace
                break
            
            replace_str: str = ""

            # NOTE(vanya): Parse syntax innards
            variable_syntax: str = regex_match.group(0)
            variable_inner_syntax: str = (
                variable_syntax
                .strip()
                .removeprefix("<!--")
                .removesuffix("-->")
                .strip()
            )

            # NOTE(vanya): Parse variable name
            requested_variable_name: str = variable_inner_syntax.removeprefix("$")

            if requested_variable_name in p_kwargs.keys():
                # NOTE(vanya): Replace the syntax source with the found value
                rendered_source = rendered_source[:regex_match.start()] + str(p_kwargs[requested_variable_name]) + rendered_source[regex_match.end():]
            else:
                rendered_source = rendered_source[:regex_match.start()] + rendered_source[regex_match.end():]
                logging.warning(f"The found variable syntax `{requested_variable_name}` was not provided to the rendering function! (Broken Python)")

        # NOTE(vanya): Replace all COMPONENT syntax with registered components until none are left
        while True:
            # NOTE(vanya): Match syntax
            regex_match = re.search(r"<!--\s*@.*?-->", rendered_source, re.S)
            
            if regex_match == None:
                # NOTE(vanya): No syntax left to replace
                break
            
            replace_str: str = ""


            # NOTE(vanya): Parse syntax innards

            component_syntax: str = regex_match.group(0)
            component_inner_syntax: str = (
                component_syntax
                .strip()
                .removeprefix("<!--")
                .removesuffix("-->")
                .strip()
            )


            # NOTE(vanya): Parse positional-arguments and key-arguments

            parts: list[str] = shlex.split(component_inner_syntax)

            if not parts:
                logging.warning(
                    f"Component syntax without a component name! `{component_syntax}`"
                )

                # NOTE(vanya): Remove malformed syntax so it isn't matched forever.
                rendered_source = (
                    rendered_source[:regex_match.start()]
                    + rendered_source[regex_match.end():]
                )
                continue

            requested_component_name: str = parts.pop(0).removeprefix("@")

            args: list = []
            kwargs: dict = {}
            
            for part in parts:
                if "=" in part:
                    key, value = part.split("=", 1)
                    kwargs[key] = value
                else:
                    args.append(part)

            if not requested_component_name:
                logging.warning(f"Component syntax without a component name! `{component_syntax}` `{requested_component_name}`")

            # NOTE(vanya): Search for a component to render the replacement
            found_requested_component: bool = False
            for component in self.components:
                if component.name == requested_component_name:
                    # NOTE(vanya): Call component rendering function with argments and renderpass parameters
                    found_requested_component = True

                    if component.callback:
                        replace_str = component.callback(*args, **kwargs)
                    else:
                        logging.warning(f"The found component `{requested_component_name}` does not have a assigned callback. (Malformed component!)")

                    break
            
            if not found_requested_component:
                # if requested_component_name in p_paste_keys:
                #     replace_str = str(p_paste_keys[requested_component_name])
                # else:
                logging.error(f"Could not find a requested component `{requested_component_name}`.")

            # NOTE(vanya): Replace the HTML source
            rendered_source = rendered_source[:regex_match.start()] + replace_str + rendered_source[regex_match.end():]

        return rendered_source


    def render_file(self, p_path: str, **p_kwargs: dict) -> str:
        with open(p_path, "r", encoding="utf-8") as f:
            return self.render(f.read(), **p_kwargs)


    def render_file_response(self, p_path: str, **p_kwargs: dict) -> HTTPResponse:
        if os.path.exists(p_path):
            return HTTPResponse.ok(self.render_file(p_path, **p_kwargs).encode("utf-8"), "text/html; charset=utf-8")
        else:
            return HTTPResponse.not_found(b"404", "text/html; charset=utf-8")


    def register_component(self, p_name: str, p_callback: ComponentCallbackType) -> None:
        new_component = Component()
        new_component.name = p_name
        new_component.callback = p_callback

        self.components.append(new_component)

        logging.debug(f"Registered component `{p_name}`")


    def register_components_from_dir(self, p_path: str) -> None:
        logging.debug(f"Scanning directory `{p_path}` to register components.")

        assert os.path.exists(p_path), "The component directory must exist!"

        for dir_path, dir_names, file_names in os.walk(p_path):
            for file_name in file_names:
                file_path: str = os.path.join(dir_path, file_name)

                if not os.path.isfile(file_path):
                    continue

                if file_name.endswith(".py"):
                    logging.debug(f"Found `{file_path}` - Attempting to import and call `register_components(app)`")
                    
                    project_root_path: str = os.path.abspath(os.getcwd())

                    if not os.path.abspath(file_path).startswith(project_root_path):
                        logging.warning(f"{file_path} is not in the same directory (or any of its children directories) and the project root - cannot import the module.")
                        continue
                    
                    module_path: str = \
                        os.path.relpath(file_path, project_root_path) \
                        .replace(os.sep, ".") \
                        .removesuffix(".py")
                    
                    module_path_has_illegal_characters: bool = False
                    for module_path_part in module_path.split("."):
                        if not is_valid_python_module_name(module_path_part):
                            module_path_has_illegal_characters = True
                            break
                    
                    if module_path_has_illegal_characters:
                        logging.warning(f"Module path `{module_path}` has illegal characters. (Each part can only have A-Z, 0-9, and underscores. And must not begin with a number)")
                        continue

                    component_registrar_module = importlib.import_module(module_path)
                    
                    if hasattr(component_registrar_module, "register_components"):
                        component_registrar_module.register_components(self)
                    else:
                        logging.error(f"Module `{module_path}` has no function `register_components(html_renderer)` which usually registers the components.")
                
                elif (
                    file_path.endswith(".html")
                    or file_path.endswith(".htm")
                ):
                    def simple_html_render_callback(
                            *args: str,
                            p_file_path: str=file_path,
                            **kwargs: str,
                    ) -> str:
                        return self.render_file(p_file_path)

                    self.register_component(
                            file_path.removeprefix(p_path).removeprefix(os.sep),
                            simple_html_render_callback,
                    )