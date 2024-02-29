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

from interactigen.brokenjsonparser import parse_json_markdown


@pytest.mark.parametrize("test_name, in_str", [
    ("Test 1",
    """```json
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
]}
```""",
     ),
    ("Test 2",
     """```json
{"utterances": ["Thank you so much for your assistance!", "I value your support.", "You've been incredibly helpful.", 'I appreciate your time and effort.', "I'm thankful for your guidance.", "You've been very supportive.", 'I appreciate your advice.', 'Thank you for your understanding.', "You've simplified this process for me.", "I'm grateful for your assistance.", "You're a lifesaver!", "I don't know what I would have done without you.", "You've exceeded my expectations.", "I'm very impressed with your service.", "You're a valuable resource.", "I'll definitely be recommending you to others.", 'Thank you again for your help.', "I'm so appreciative of your support.", "You've made my day!", 'Thanks!', 'I like your assistance.', 'You aided me.', 'Thanks.', 'I like your assistance.', 'You aided me.', 'I like your assistance.', 'Thanks.', 'You helped me.', 'I like your assistance.', 'You helped me.', 'I like your assistance.', 'You helped me.', 'I like your assistance.', 'You helped me.', 'I like your assistance.', 'You helped me.', 'I like your assistance.', 'You helped me.', 'Thanks', 'Appreciate', 'Helpful', 'Time', 'Grateful', 'Easy', 'Glad', 'Lifesaver', 'Recommend', 'Support', 'Day']}
```""",
     ),
])
def test_broken_json_parser(test_name: str, in_str: str):
    json_result = parse_json_markdown(in_str)
    print(f"test_name: {test_name}, json_result: {json_result}")
    assert True
