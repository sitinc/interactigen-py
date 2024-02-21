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

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tracers.context import tracing_v2_enabled

import logging

# Initialize the logger.
log = logging.getLogger('interactigenLogger')

sys_prompt = """You are a helpful assistant that generates high-quality training data for use with voice and chat 
bots."""


# Define Generate Phrase Utterances Response and Parser
class PhraseUtterances(BaseModel):
    utterances: list[str] = Field(description="The array of generated utterances.", examples=["Hello", "Hi", "Hey"])


gen_phrase_parser = JsonOutputParser(pydantic_object=PhraseUtterances)

gen_phrase_base_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=(sys_prompt+'\n\n'+gen_phrase_parser.get_format_instructions())),
        HumanMessagePromptTemplate.from_template("Please generate {quantity} semantically diverse ways {base_phrase}."),
    ]
)

gen_phrase_transform_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=(sys_prompt+'\n\n'+gen_phrase_parser.get_format_instructions())),
        HumanMessagePromptTemplate.from_template("Here is a list of utterances:\n\n{utterances}\n\nPlease repeat "
                                                 "these examples, but {transform_phrase}"),
    ]
)


class Interactigen:
    """
    Interactigen client interface.
    """

    def __init__(self,
                 *,
                 model: BaseChatModel,
                 ):
        self.model = model

    def generate_phrase_init_utterances(self,
                                        *,
                                        base_phrase: str,
                                        quantity: int,
                                        **kwargs) -> list[str]:
        base_chain = gen_phrase_base_prompt | self.model | gen_phrase_parser

        base_chain_result = base_chain.invoke({
            "sys_prompt": sys_prompt,
            "base_phrase": base_phrase,
            "quantity": quantity,
            **kwargs,
        })
        return base_chain_result['utterances']

    def generate_phrase_transform_utterances(self,
                                             *,
                                             utterances: list[str],
                                             transform_phrase: str,
                                             **kwargs) -> list[str]:
        transform_chain = gen_phrase_transform_prompt | self.model | gen_phrase_parser

        transform_chain_result = transform_chain.invoke({
            "sys_prompt": sys_prompt,
            "utterances": utterances,
            "transform_phrase": transform_phrase,
            **kwargs,
        })
        return transform_chain_result['utterances']

    def generate_phrase_transform_all(self,
                                      *,
                                      utterances: list[str],
                                      **kwargs) -> list[str]:
        all_transforms = [
            'flip bigrams or trigrams',
            'swap common synonyms',
        ]
        all_transforms_result = [
            result for in_entry in all_transforms
            for result in self.generate_phrase_transform_utterances(
                utterances=utterances,
                transform_phrase=in_entry,
                **kwargs,
            )]

        return all_transforms_result

    def generate_phrase_transform_voice(self,
                                        *,
                                        utterances: list[str],
                                        **kwargs) -> list[str]:
        voice_transforms = [
            'introduce common speech recognition mistranslations',
            'introduce common audio loss mistranslations',
        ]
        voice_transforms_result = [
            result for in_entry in voice_transforms
            for result in self.generate_phrase_transform_utterances(
                utterances=utterances,
                transform_phrase=in_entry,
                **kwargs,
            )]

        return voice_transforms_result

    def generate_phrase_transform_chat(self,
                                       *,
                                       utterances: list[str],
                                       **kwargs) -> list[str]:
        chat_transforms = [
            'introduce common spelling mistakes',
            'introduce common emojis',
        ]
        chat_transforms_result = [
            result for in_entry in chat_transforms
            for result in self.generate_phrase_transform_utterances(
                utterances=utterances,
                transform_phrase=in_entry,
                **kwargs,
            )]

        return chat_transforms_result

    def generate_phrase_base_utterances(self,
                                        *,
                                        base_phrase: str,
                                        quantity: int,
                                        **kwargs) -> list[str]:
        init_utterances = self.generate_phrase_init_utterances(base_phrase=base_phrase, quantity=quantity)

        base_transforms = [
            'sound more casual and use half the words',
            'use one to three words',
        ]
        transformed_utterances = [
            result for in_entry in base_transforms
            for result in self.generate_phrase_transform_utterances(
                utterances=init_utterances,
                transform_phrase=in_entry,
                **kwargs,
            )]

        return init_utterances+transformed_utterances

    def generate_phrase_utterances(self,
                                   *,
                                   base_phrase: str,
                                   base_quantity: int = 10,
                                   media_type: str = 'voice',
                                   lc_project: str = None,
                                   **kwargs) -> list[str]:
        with tracing_v2_enabled(lc_project):
            final_utterances: list[str] = []
            base_utterances = self.generate_phrase_base_utterances(base_phrase=base_phrase, quantity=base_quantity)
            final_utterances = final_utterances+base_utterances

            all_transform_utterances = self.generate_phrase_transform_all(utterances=base_utterances)
            final_utterances = final_utterances+all_transform_utterances

            if media_type == 'voice':
                voice_transform_utterances = self.generate_phrase_transform_voice(utterances=base_utterances)
                final_utterances = final_utterances+voice_transform_utterances
            else:
                chat_transform_utterances = self.generate_phrase_transform_chat(utterances=base_utterances)
                final_utterances = final_utterances+chat_transform_utterances

            return final_utterances
