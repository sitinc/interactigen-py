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

import pytest

from interactigen.brokenjsonparser import fix_single_quote_strings


@pytest.mark.parametrize("test_name, in_str, expected", [
    #  Test 1
    ("Test 1",
     """
{"utterances": [
    "Fank you, bot!",
    "You're a life saver!",
    'I weally appweeciate youw help.',
    "You've been so he'pful.",
    'Fanks fow youw time.',
    'That was weally he'pful.',
    "I'm so g'ateful fow youw help.",
    "You'we the best!",
    'Fank you fow youw patience.',
    "I couldn't have done it without you.",
    "You'we a stah!",
    "You'we a genius!"
]}'
""",
     """
{"utterances": [
    "Fank you, bot!",
    "You're a life saver!",
    "I weally appweeciate youw help.",
    "You've been so he'pful.",
    "Fanks fow youw time.",
    "That was weally he'pful.",
    "I'm so g'ateful fow youw help.",
    "You'we the best!",
    "Fank you fow youw patience.",
    "I couldn't have done it without you.",
    "You'we a stah!",
    "You'we a genius!"
]}'
""",
     ),
    #  Test 2
    ("Test 2",
     """
{"utterances": [
    "Fank you, bot!",
    "You're a life saver!",
    'I weally appweeciate youw help.',
    "You've been so he'pful.",
    'Fanks fow youw time.',
    'That was weally he'pful.',
    "I'm so g'ateful fow youw help.",
    "You'we the best!",
    'Fank you fow youw patience.',
    "I couldn't have done it without you.",
    "You'we a stah!",
    'You'we a genius!'
]}
""",
     """
{"utterances": [
    "Fank you, bot!",
    "You're a life saver!",
    "I weally appweeciate youw help.",
    "You've been so he'pful.",
    "Fanks fow youw time.",
    "That was weally he'pful.",
    "I'm so g'ateful fow youw help.",
    "You'we the best!",
    "Fank you fow youw patience.",
    "I couldn't have done it without you.",
    "You'we a stah!",
    "You'we a genius!"
]}
""",
     ),
    #  Test 3
    ("Test 3",
     """
{"utterances": [
    "Fank you, bot!",
    "You're a life saver!",
    'I weally appweeciate youw help.',
    "You've been so he'pful.",
    'Fanks fow youw time.',
    'That was weally he'pful.',
    "I'm so g'ateful fow youw help.",
    "You'we the best!",
    'Fank you fow youw patience.',
    "I couldn't have done it without you.",
    "You'we a stah!",
    'You'we a genius!']}
""",
     """
{"utterances": [
    "Fank you, bot!",
    "You're a life saver!",
    "I weally appweeciate youw help.",
    "You've been so he'pful.",
    "Fanks fow youw time.",
    "That was weally he'pful.",
    "I'm so g'ateful fow youw help.",
    "You'we the best!",
    "Fank you fow youw patience.",
    "I couldn't have done it without you.",
    "You'we a stah!",
    "You'we a genius!"]}
""",
     ),
])
def test_broken_json_parser(test_name: str, in_str: str, expected: str):
    result = fix_single_quote_strings(in_str)
    if result != expected:
        print(f"{test_name}: result: {result}")
    assert result == expected
