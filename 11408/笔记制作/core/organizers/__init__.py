# -*- coding: utf-8 -*-
"""Organizer 注册表：新增笔记类型 = 新建 organizer + parser 并在这里登记。"""
from .base import Organizer
from .k408 import K408Organizer
from .math_lecture import MathLectureOrganizer
from .math_section import MathSectionOrganizer
from .k408_chapter import K408ChapterOrganizer
from .prob_chapter import ProbChapterOrganizer

ORGANIZERS = {o.type: o for o in (
    K408Organizer(), MathLectureOrganizer(), MathSectionOrganizer(),
    K408ChapterOrganizer(), ProbChapterOrganizer(),
)}

TYPES = list(ORGANIZERS)