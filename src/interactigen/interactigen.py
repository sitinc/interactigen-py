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
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.language_models import BaseLanguageModel
from langchain_core.exceptions import OutputParserException
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.language_models.llms import BaseLLM
from langchain_core.tracers.context import tracing_v2_enabled

from .brokenjsonparser import BrokenJsonOutputParser

import random
import time
import logging

# Initialize the logger.
log = logging.getLogger('interactigenLogger')


def retry_with_exponential_backoff(
        func,
        initial_delay: float = 1,
        exponential_base: float = 2,
        jitter: bool = True,
        max_retries: int = 3,
        errors: tuple = (OutputParserException,),
):
    """Retry a function with exponential backoff."""

    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay

        # Loop until a successful response or max_retries is hit or an exception is raised
        while True:
            try:
                return func(*args, **kwargs)

            # Retry on specific errors
            except errors as e:
                log.error(f"Caught exception: {e}")

                # Increment retries
                num_retries += 1

                # Check if max retries has been reached
                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )

                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())

                # Sleep for the delay
                time.sleep(delay)

            # Raise exceptions for any errors not specified
            except Exception as e:
                raise e

    return wrapper


# The common system prompt heading.
sys_prompt = "You are a helpful assistant that generates high-quality training data for use with voice and text bots."


# Define Generate Phrase Utterances Response Format and Parser
class PhraseUtterances(BaseModel):
    utterances: list[str] = Field(description="The array of generated utterances.", examples=["Hello", "Hi", "Hey"])


gen_phrase_parser = BrokenJsonOutputParser(pydantic_object=PhraseUtterances)

# Define the initial prompt for generating base utterances.
gen_phrase_init_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=(sys_prompt+'\n\n'+gen_phrase_parser.get_format_instructions())),
        HumanMessagePromptTemplate.from_template("Please generate {quantity} semantically diverse ways {base_phrase}."),
    ]
)

# Define the transform prompt to apply to base utterances.
gen_phrase_transform_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=(sys_prompt+'\n\n'+gen_phrase_parser.get_format_instructions())),
        HumanMessagePromptTemplate.from_template("Here is a list of utterances:\n\n{utterances}\n\nPlease repeat "
                                                 "these examples, but {transform_phrase}"),
    ]
)

# Apply these to the initially generated utterances to form the base utterances for each downstream transform.
transform_phrases_base = [
    'sound more casual and use half the words',
    'use one to three words',
]
# Apply these to all base utterances regardless of media type.
transform_phrases_all = [
    'flip bigrams or trigrams',
    'swap common synonyms',
]
# Apply these to all voice media type utterances.
transform_phrases_voice = [
    'introduce common speech recognition mistranslations',
    'introduce common audio loss mistranslations',
]
# Apply these to all text media type utterances.
transform_phrases_text = [
    'introduce common spelling mistakes',
    'introduce common emojis',
]


class Interactigen:
    """
    Interactigen client interface.
    """

    def __init__(self,
                 *,
                 model: BaseLanguageModel,
                 ):
        """
        Create a new instance.
        :param model: The LangChain base chat model.
        """
        self.model = model
        self.type = 'chat' if isinstance(model, BaseChatModel) else ('llm' if isinstance(model, BaseLLM) else None)
        if self.type is None:
            raise Exception('Unknown LangChain model type')

    def __str__(self):
        """
        Return a human-readable string.
        :return: a human-readable string.
        """
        return f"Interactigen(source={self.type})"

    def __repr__(self):
        """
        Return a human-readable string.
        :return: a human-readable string.
        """
        return f"Interactigen(source={self.type!r})"

    @retry_with_exponential_backoff
    def generate_phrase_init_utterances(self,
                                        *,
                                        base_phrase: str,
                                        quantity: int,
                                        **kwargs) -> list[str]:
        """
        Generate a list of semantically diverse utterances from a base phrase.
        :param base_phrase: The base phrase.
        :param quantity: The quantity of semantically diverse utterances.
        :param kwargs: Additional parameters to pass into the LangChain chat model.
        :return: an array of semantically diverse utterances.
        """
        base_chain = gen_phrase_init_prompt | self.model | gen_phrase_parser

        base_chain_result = base_chain.invoke({
            "sys_prompt": sys_prompt,
            "base_phrase": base_phrase,
            "quantity": quantity,
            **kwargs,
        })
        return base_chain_result['utterances']

    @retry_with_exponential_backoff
    def generate_phrase_transforms(self,
                                   *,
                                   utterances: list[str],
                                   transform_phrase: str,
                                   **kwargs) -> list[str]:
        """
        Generate a list of transformed utterances from an input source and transformation instruction.
        :param utterances: The utterances to transform.
        :param transform_phrase: The transformation instruction phrase.
        :param kwargs: Additional parameters to pass into the LangChain chat model.
        :return: an array of transformed utterances.
        """
        transform_chain = gen_phrase_transform_prompt | self.model | gen_phrase_parser

        transform_chain_result = transform_chain.invoke({
            "sys_prompt": sys_prompt,
            "utterances": utterances,
            "transform_phrase": transform_phrase,
            **kwargs,
        })
        return transform_chain_result['utterances']

    def generate_phrase_transforms_all(self,
                                       *,
                                       utterances: list[str],
                                       **kwargs) -> list[str]:
        """
        Generate a list of transformed utterances based on rules to apply to all media types.
        :param utterances: The utterances to transform.
        :param kwargs: Additional parameters to pass into the LangChain chat model.
        :return: an array of transformed utterances.
        """
        all_transforms_result = [
            result for in_entry in transform_phrases_all
            for result in self.generate_phrase_transforms(
                utterances=utterances,
                transform_phrase=in_entry,
                **kwargs,
            )]

        return all_transforms_result

    def generate_phrase_transforms_voice(self,
                                         *,
                                         utterances: list[str],
                                         **kwargs) -> list[str]:
        """
        Generate a list of transformed utterances based on rules to apply to voice-only media types.
        :param utterances: The utterances to transform.
        :param kwargs: Additional parameters to pass into the LangChain chat model.
        :return: an array of transformed utterances.
        """
        voice_transforms_result = [
            result for in_entry in transform_phrases_voice
            for result in self.generate_phrase_transforms(
                utterances=utterances,
                transform_phrase=in_entry,
                **kwargs,
            )]

        return voice_transforms_result

    def generate_phrase_transforms_text(self,
                                        *,
                                        utterances: list[str],
                                        **kwargs) -> list[str]:
        """
        Generate a list of transformed utterances based on rules to apply to text-only media types.
        :param utterances: The utterances to transform.
        :param kwargs: Additional parameters to pass into the LangChain chat model.
        :return: an array of transformed utterances.
        """
        chat_transforms_result = [
            result for in_entry in transform_phrases_text
            for result in self.generate_phrase_transforms(
                utterances=utterances,
                transform_phrase=in_entry,
                **kwargs,
            )]

        return chat_transforms_result

    def generate_phrase_base_utterances(self,
                                        *,
                                        base_phrase: str,
                                        init_quantity: int,
                                        **kwargs) -> list[str]:
        """
        Generate a list of base + augmented semantically diverse utterances from a base phrase.
        :param base_phrase: The base phrase.
        :param init_quantity: The initial quantity of semantically diverse utterances before any transformations.
        :param kwargs: Additional parameters to pass into the LangChain chat model.
        :return: an array of semantically diverse utterances.
        """
        init_utterances = self.generate_phrase_init_utterances(base_phrase=base_phrase, quantity=init_quantity)

        transformed_utterances = [
            result for in_entry in transform_phrases_base
            for result in self.generate_phrase_transforms(
                utterances=init_utterances,
                transform_phrase=in_entry,
                **kwargs,
            )]

        return init_utterances+transformed_utterances

    def generate_phrase_utterances(self,
                                   *,
                                   base_phrase: str,
                                   init_quantity: int = 10,
                                   media_type: str = 'voice',
                                   lc_project: str = None,
                                   **kwargs) -> list[str]:
        """
        Generate a fully augmented list of semantically diverse utterances from a base phrase.
        :param base_phrase: The base phrase.
        :param init_quantity: The initial quantity of semantically diverse utterances before any transformations.
        :param media_type: The intended media type for the phrases.  Default is 'voice'.
        :param lc_project: The LangChain project used for LangSmith tracing.  Default is None (Default in LangSmith).
        :param kwargs: Additional parameters to pass into the LangChain chat model.
        :return: an array of semantically diverse utterances.
        """
        with tracing_v2_enabled(lc_project):
            final_utterances: list[str] = []
            base_utterances = self.generate_phrase_base_utterances(
                base_phrase=base_phrase,
                init_quantity=init_quantity,
                **kwargs,
            )
            final_utterances = final_utterances+base_utterances

            all_transform_utterances = self.generate_phrase_transforms_all(utterances=base_utterances, **kwargs)
            final_utterances = final_utterances+all_transform_utterances

            if media_type == 'voice':
                voice_transform_utterances = self.generate_phrase_transforms_voice(utterances=base_utterances, **kwargs)
                final_utterances = final_utterances+voice_transform_utterances
            else:  # media_type == 'text'
                chat_transform_utterances = self.generate_phrase_transforms_text(utterances=base_utterances, **kwargs)
                final_utterances = final_utterances+chat_transform_utterances

            return final_utterances
