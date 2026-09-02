# -*- coding: utf-8 -*-
"""Parser 注册表（与 ORGANIZERS 同 key）。"""
from .base import Parser
from .k408 import K408Parser
from .math_lecture import MathLectureParser
from .math_section import MathSectionParser
from .k408_chapter import K408ChapterParser
from .prob_chapter import ProbChapterParser

PARSERS = {p.type: p for p in (K408Parser(), MathLectureParser(), MathSectionParser(),
                               K408ChapterParser(), ProbChapterParser())}