# MIT License
#
# Copyright (c) 2024, Justin Randall, Smart Interactive Transformations Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from interacticore import BrokenJsonOutputParser, ChatCommand
from interactigen import PhraseUtterances

# The system prompt heading.
sys_prompt_hdr = ("You are a helpful assistant that generates high-quality training data for use with voice and text "
                  "bots.")

# The user prompt template.
user_prompt_tmpl = "Please generate {quantity} semantically diverse ways {base_phrase}."

# The output parser and final system prompt.
output_parser = BrokenJsonOutputParser(pydantic_object=PhraseUtterances)
sys_prompt = f"{sys_prompt_hdr}.\n\n{output_parser.get_format_instructions()}"


class GenNewPhrasings(ChatCommand):
    """
    Command object for generating new phrases based on instructions.
    """
    def __init__(self,
                 *,
                 session_id: str = None,
                 base_phrase: str = None,
                 quantity: int = None,
                 ):
        """
        Construct a new instance.
        :param session_id: The session ID.
        :param base_phrase: The base instructional phrase.
        :param quantity: The phrasing quantity.
        """
        super().__init__(
            session_id=session_id,
            cmd_name='GenNewPhrasings',
            sys_prompt=sys_prompt,
            user_prompt_tmpl=user_prompt_tmpl,
            output_parser=output_parser,
        )
        if base_phrase is None:
            raise Exception("base_phrase is required")
        if quantity is None:
            raise Exception("quantity is required")

        self.base_phrase = base_phrase
        self.quantity = quantity
        self.inputs = {
            "base_phrase": self.base_phrase,
            "quantity": self.quantity,
        }

    def __str__(self):
        return (f"GenNewPhrasings(super={super().__str__()}" +
                f", base_phrase={self.base_phrase}" +
                f", quantity={self.quantity}" +
                ")")

    def __repr__(self):
        return (f"GenNewPhrasings(super={super().__repr__()}" +
                f", base_phrase={self.base_phrase!r}" +
                f", quantity={self.quantity!r}" +
                ")")
