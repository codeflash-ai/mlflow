import string
from typing import Any


class PromptTemplate:
    """A prompt template for a language model.

    A prompt template consists of an array of strings that will be concatenated together. It accepts
    a set of parameters from the user that can be used to generate a prompt for a language model.

    The template can be formatted using f-strings.

    Example:

        .. code-block:: python

            from mlflow.metrics.genai.prompt_template import PromptTemplate

            # Instantiation using initializer
            prompt = PromptTemplate(template_str="Say {foo} {baz}")

            # Instantiation using partial_fill
            prompt = PromptTemplate(template_str="Say {foo} {baz}").partial_fill(foo="bar")

            # Format the prompt
            prompt.format(baz="qux")
    """

    def __init__(self, template_str: str | list[str]):
        self.template_strs = [template_str] if isinstance(template_str, str) else template_str

    @property
    def variables(self):
        return {
            fname
            for template_str in self.template_strs
            for _, fname, _, _ in string.Formatter().parse(template_str)
            if fname
        }

    def format(self, **kwargs: Any) -> str:
        safe_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        formatted_strs = []
        # Cache the keys for fast membership test instead of re-creating dict_keys() on each loop
        safe_keys = set(safe_kwargs.keys())
        formatter_parse = string.Formatter().parse
        for template_str in self.template_strs:
            # Avoid repeated string.Formatter() creation, and precompute parse once
            extracted_variables = []
            # Parsing and collecting field names efficiently
            for _, fname, _, _ in formatter_parse(template_str):
                if fname:
                    extracted_variables.append(fname)
            # Use set.issubset instead of 'all', this is significantly faster for many variables
            if set(extracted_variables).issubset(safe_keys):
                formatted_strs.append(template_str.format(**safe_kwargs))
        return "".join(formatted_strs)

    def partial_fill(self, **kwargs: Any) -> "PromptTemplate":
        safe_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        new_template_strs = []
        for template_str in self.template_strs:
            extracted_variables = [
                fname for _, fname, _, _ in string.Formatter().parse(template_str) if fname
            ]
            safe_available_kwargs = {
                k: safe_kwargs.get(k, "{" + k + "}") for k in extracted_variables
            }
            new_template_strs.append(template_str.format_map(safe_available_kwargs))

        return PromptTemplate(template_str=new_template_strs)

    def __str__(self) -> str:
        return "".join(self.template_strs)
