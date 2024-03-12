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
user_prompt_tmpl = ("Here is a list of utterances:\n\n{utterances}\n\nPlease repeat these examples, "
                    "but {transform_phrase}")

# The output parser and final system prompt.
output_parser = BrokenJsonOutputParser(pydantic_object=PhraseUtterances)
sys_prompt = f"{sys_prompt_hdr}.\n\n{output_parser.get_format_instructions()}"


class GenTransformedPhrasings(ChatCommand):
    """
    Command object for transforming utterances based on instructions based on instructions.
    """
    def __init__(self,
                 *,
                 session_id: str = None,
                 utterances: list[str] = None,
                 transform_phrase: str = None,
                 ):
        """
        Construct a new instance.
        :param session_id: The session ID.
        :param utterances: The utterances.
        :param transform_phrase: The phrase instructions to transform the utterances.
        """
        super().__init__(
            session_id=session_id,
            cmd_name='GenTransformedPhrasings',
            sys_prompt=sys_prompt,
            user_prompt_tmpl=user_prompt_tmpl,
            output_parser=output_parser,
        )
        if utterances is None:
            raise Exception("utterances is required")
        if transform_phrase is None:
            raise Exception("transform_phrase is required")

        self.utterances = utterances
        self.transform_phrase = transform_phrase
        self.inputs = {
            "utterances": self.utterances,
            "transform_phrase": self.transform_phrase,
        }

    def __str__(self):
        return (f"GenTransformedPhrasings(super={super().__str__()}" +
                f", utterances={self.utterances}" +
                f", transform_phrase={self.transform_phrase}" +
                ")")

    def __repr__(self):
        return (f"GenTransformedPhrasings(super={super().__repr__()}" +
                f", utterances={self.utterances!r}" +
                f", transform_phrase={self.transform_phrase!r}" +
                ")")
