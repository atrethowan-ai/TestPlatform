"""
validation_service.py
Authoring quiz validation — used by GUI and CLI.
Returns (errors: list[str], warnings: list[str])
"""
import re
import os
import json
from pathlib import Path

SUPPORTED_TYPES = {'multiple_choice', 'short_answer', 'paragraph', 'audio_short_answer'}
STIMULUS_SET_TYPE = 'stimulus_set'
DECISION_TREE_TYPE = 'decision_tree'
STIMULUS_CHILD_SUPPORTED_TYPES = {'multiple_choice', 'short_answer'}
STIMULUS_SET_ALLOWED_CATEGORIES = {
    'Reading & Listening Comprehension',
    'General Knowledge & Science',
    'Social Development',
}
DECISION_TREE_ALLOWED_CATEGORY = 'Social Development'
# Quiz-level taxonomy rule: one category per quiz. Subcategory/skill are validated per question.
REQUIRED_TOP_LEVEL = ['id', 'title', 'ageGroup', 'category', 'difficulty_level', 'sections']

# Canonical quiz taxonomy — category → subcategory → [skills]
DEFAULT_TAXONOMY = {
    "Mathematics & Numeracy": {
        "Number Sense": ["Counting", "Number recognition", "Place value", "Comparing numbers", "Number sequences", "Rounding"],
        "Addition & Subtraction": ["Basic addition facts", "Basic subtraction facts", "Mental arithmetic", "Missing number problems", "Multi-step arithmetic"],
        "Multiplication & Division": ["Times tables", "Division facts", "Inverse operations", "Multiplication patterns"],
        "Fractions & Decimals": ["Fraction recognition", "Equivalent fractions", "Fraction comparison", "Simple fraction operations", "Decimal basics"],
        "Measurement": ["Time", "Length", "Mass / weight", "Volume / capacity", "Area", "Temperature"],
        "Geometry": ["Shape recognition", "Angles", "Symmetry", "Coordinates", "Spatial reasoning"],
        "Data & Probability": ["Reading graphs", "Interpreting tables", "Simple probability", "Data comparison"],
        "Word Problems": ["Single-step problems", "Multi-step problems", "Real-world scenarios", "Estimation problems"],
    },
    "Spelling & Phonics": {
        "Phonemic Awareness": ["Beginning sounds", "Ending sounds", "Middle vowel sounds", "Sound blending", "Sound segmentation"],
        "Phonics Patterns": ["Consonant blends", "Digraphs", "Vowel teams", "Silent letters", "R-controlled vowels"],
        "Basic Spelling": ["CVC words", "High-frequency words", "Sight words", "Plurals", "Simple suffixes"],
        "Advanced Spelling": ["Prefixes", "Suffixes", "Root words", "Word families", "Irregular spellings"],
        "Homophones & Confusables": ["Homophones", "Frequently confused words"],
        "Dictation": ["Word dictation", "Sentence dictation", "Context-based spelling"],
    },
    "Reading & Listening Comprehension": {
        "Literal Comprehension": ["Fact recall", "Who / what / where questions", "Detail identification"],
        "Vocabulary in Context": ["Meaning of words", "Synonyms", "Antonyms", "Context clues"],
        "Narrative Understanding": ["Sequence of events", "Character motivation", "Setting identification"],
        "Informational Text": ["Key facts", "Topic identification", "Explanation understanding"],
        "Inference": ["Implicit meaning", "Predicting outcomes", "Drawing conclusions"],
        "Main Idea & Theme": ["Main idea", "Supporting details", "Theme identification"],
        "Listening Comprehension": ["Recall from spoken text", "Follow instructions", "Auditory story understanding"],
    },
    "Language Conventions": {
        "Sentence Structure": ["Identifying sentences", "Fragments vs sentences", "Combining sentences"],
        "Parts of Speech": ["Nouns", "Verbs", "Adjectives", "Adverbs", "Pronouns"],
        "Verb Usage": ["Tense", "Subject-verb agreement"],
        "Punctuation": ["Full stops / periods", "Commas", "Question marks", "Apostrophes", "Quotation marks"],
        "Capitalisation": ["Sentence beginnings", "Proper nouns", "Titles"],
        "Word Usage": ["Correct word choice", "Grammar correction"],
    },
    "Writing": {
        "Sentence Writing": ["Complete sentences", "Sentence expansion", "Sentence correction"],
        "Descriptive Writing": ["Describe a picture", "Describe an object", "Describe an event"],
        "Narrative Writing": ["Story beginning", "Story continuation", "Story retelling"],
        "Persuasive Writing": ["Opinion statements", "Reasoned argument", "Supporting details"],
        "Informational Writing": ["Explaining a process", "Summarising information", "Giving instructions"],
        "Writing Mechanics": ["Spelling in context", "Punctuation in writing", "Paragraph structure"],
        "Editing & Revision": ["Correcting mistakes", "Improving clarity", "Rewriting sentences"],
    },
    "Logic & Reasoning": {
        "Pattern Recognition": ["Number patterns", "Visual patterns", "Shape sequences"],
        "Classification": ["Odd one out", "Category grouping"],
        "Analogies": ["Verbal analogies", "Concept analogies"],
        "Deductive Reasoning": ["If/then logic", "Elimination problems", "Ranking problems"],
        "Spatial Reasoning": ["Rotating shapes", "Mirror images", "Position relationships"],
        "Problem Solving": ["Puzzle questions", "Strategy problems"],
    },
    "General Knowledge & Science": {
        "Life Science": ["Animals", "Plants", "Habitats", "Human body"],
        "Earth Science": ["Weather", "Seasons", "Landforms", "Oceans"],
        "Physical Science": ["Forces", "Energy", "Materials", "Simple machines"],
        "Space Science": ["Planets", "Sun and moon", "Stars", "Space exploration"],
        "Environment & Ecology": ["Ecosystems", "Food chains", "Conservation"],
        "Geography": ["Continents", "Maps", "Countries", "Landmarks"],
        "History & Culture": ["Historical figures", "Important events", "Civilisations", "Australian history basics"],
    },
}


def _load_master_taxonomy() -> dict:
    """Load taxonomy from the active grading architecture docs.

    Supports either a `canonical-taxonomy-json` or `json` code block.
    Falls back to DEFAULT_TAXONOMY if loading/parsing/validation fails.
    """
    docs_root = Path(__file__).resolve().parents[4] / "docs" / "grading_architecture"
    candidate_paths = [
        docs_root / "final_master_taxonomy.md",
        docs_root / "upgrade set" / "final_master_taxonomy.md",
        docs_root / "master_taxonomy.md",
    ]

    for master_path in candidate_paths:
        if not master_path.exists():
            continue

        try:
            text = master_path.read_text(encoding='utf-8')
        except OSError:
            continue

        match = re.search(
            r"```(?:canonical-taxonomy-json|json)\s*(\{.*?\})\s*```",
            text,
            flags=re.DOTALL,
        )
        if not match:
            continue

        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue

        if not isinstance(data, dict) or not data:
            continue

        is_valid = True
        for category, subcategories in data.items():
            if not isinstance(category, str) or not category.strip():
                is_valid = False
                break
            if not isinstance(subcategories, dict) or not subcategories:
                is_valid = False
                break
            for subcategory, skills in subcategories.items():
                if not isinstance(subcategory, str) or not subcategory.strip():
                    is_valid = False
                    break
                if not isinstance(skills, list) or not skills:
                    is_valid = False
                    break
                if any(not isinstance(skill, str) or not skill.strip() for skill in skills):
                    is_valid = False
                    break
            if not is_valid:
                break

        if is_valid:
            return data

    return DEFAULT_TAXONOMY


TAXONOMY = _load_master_taxonomy()

DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
LATEX_DELIM_RE = re.compile(r'(\$\$?|\\\\\(|\\\\\)|\\\\\[|\\\\\])')
UNICODE_OPERATOR_RE = re.compile(r'[−×÷]')
MOJIBAKE_MARKERS = ("â", "Ã", "Â", "�")


def _has_mojibake(text: object) -> bool:
    if not isinstance(text, str):
        return False
    return any(marker in text for marker in MOJIBAKE_MARKERS)


def _validate_prompt_parts(question_id: str, prompt_parts: object, errors: list, warnings: list):
    if not isinstance(prompt_parts, list) or len(prompt_parts) == 0:
        errors.append(f"Question '{question_id}' has invalid 'promptParts' (must be a non-empty array).")
        return

    for idx, part in enumerate(prompt_parts):
        label = f"Question '{question_id}' promptParts[{idx}]"
        if not isinstance(part, dict):
            errors.append(f"{label} must be an object.")
            continue

        ptype = part.get('type')
        if ptype == 'text':
            text = part.get('text')
            if not isinstance(text, str) or not text.strip():
                errors.append(f"{label} text part must include non-empty 'text'.")
            if _has_mojibake(text):
                errors.append(f"{label} contains mojibake artifacts.")
        elif ptype == 'math':
            pformat = part.get('format')
            source = part.get('source')
            display = part.get('display', 'inline')
            alt_text = part.get('altText')

            if pformat != 'latex':
                errors.append(f"{label} math part must set format='latex'.")
            if not isinstance(source, str) or not source.strip():
                errors.append(f"{label} math part must include non-empty 'source'.")
            if display not in ('inline', 'block'):
                errors.append(f"{label} math part display must be 'inline' or 'block'.")
            if not isinstance(alt_text, str) or not alt_text.strip():
                errors.append(f"{label} math part must include non-empty 'altText'.")

            if isinstance(source, str) and LATEX_DELIM_RE.search(source):
                errors.append(f"{label} math source must not include delimiters like $, $$, \\(...\\), \\[...\\].")
            if _has_mojibake(source) or _has_mojibake(alt_text):
                errors.append(f"{label} contains mojibake artifacts.")
        else:
            errors.append(f"{label} has unsupported type '{ptype}'. Use 'text' or 'math'.")


def _validate_subcategory_and_skill(
    *,
    qid: str,
    category: str,
    subcategory_value: object,
    skill_value: object,
    errors: list,
):
    q_subcategory = subcategory_value.strip() if isinstance(subcategory_value, str) else ''
    q_skill = skill_value.strip() if isinstance(skill_value, str) else ''

    if not q_subcategory:
        errors.append(f"Question '{qid}' missing 'subcategory'.")
    elif category and category in TAXONOMY:
        valid_subcats = TAXONOMY.get(category, {})
        if q_subcategory not in valid_subcats:
            valid_list = ', '.join(f"'{s}'" for s in valid_subcats.keys())
            errors.append(
                f"Question '{qid}' has invalid subcategory '{q_subcategory}' for category '{category}'. "
                f"Must be one of: {valid_list}"
            )

    if not q_skill:
        errors.append(f"Question '{qid}' missing 'skill'.")


def _validate_standard_question(
    *,
    q: object,
    sid: str,
    position_label: str,
    category: str,
    errors: list,
    warnings: list,
    question_ids: set,
    structured_math_enabled: bool,
    allowed_types: set | None = None,
) -> int:
    if not isinstance(q, dict):
        errors.append(f"Section '{sid}' {position_label} is not an object.")
        return 0

    qid = q.get('id', '').strip() if isinstance(q.get('id'), str) else ''
    qtype = q.get('type', '').strip() if isinstance(q.get('type'), str) else ''
    qprompt = q.get('prompt', '')
    qprompt_parts = q.get('promptParts')

    if not qid:
        errors.append(f"Section '{sid}' {position_label} missing 'id'.")
    elif qid in question_ids:
        errors.append(f"Duplicate question id: '{qid}'.")
    else:
        question_ids.add(qid)

    if not qtype:
        errors.append(f"Question '{qid}' missing 'type'.")
        return 0

    _validate_subcategory_and_skill(
        qid=qid,
        category=category,
        subcategory_value=q.get('subcategory'),
        skill_value=q.get('skill'),
        errors=errors,
    )

    if qtype not in SUPPORTED_TYPES:
        warnings.append(f"WARNING: Question '{qid}' has unsupported type: '{qtype}'.")
        return 0

    if allowed_types is not None and qtype not in allowed_types:
        allowed = ', '.join(sorted(allowed_types))
        errors.append(
            f"Question '{qid}' has unsupported type '{qtype}' in this container. "
            f"Allowed types: {allowed}."
        )
        return 0

    if not isinstance(qprompt, str):
        errors.append(f"Question '{qid}' has invalid 'prompt' (must be a string).")
    elif not qprompt.strip() and not qprompt_parts:
        errors.append(f"Question '{qid}' must include non-empty 'prompt' or valid 'promptParts'.")

    if _has_mojibake(qprompt):
        errors.append(f"Question '{qid}' prompt contains mojibake artifacts.")

    if isinstance(qprompt, str) and UNICODE_OPERATOR_RE.search(qprompt):
        warnings.append(
            f"WARNING: Question '{qid}' prompt uses Unicode math operators (− × ÷). "
            f"Prefer ASCII operators in plain text or use promptParts math with LaTeX source."
        )

    if qprompt_parts is not None:
        if not structured_math_enabled:
            errors.append(
                f"Question '{qid}' uses 'promptParts' but structured math is disabled "
                f"(set QUIZ_ENABLE_STRUCTURED_MATH=1 to enable)."
            )
        _validate_prompt_parts(qid, qprompt_parts, errors, warnings)

    if qtype == 'multiple_choice':
        choices = q.get('choices', [])
        if not isinstance(choices, list) or len(choices) < 2:
            errors.append(f"Question '{qid}' (multiple_choice) must have at least 2 choices.")
        for k, choice in enumerate(choices or []):
            if _has_mojibake(choice):
                errors.append(f"Question '{qid}' choice index {k} contains mojibake artifacts.")
        answer_key = q.get('answerKey', '').strip() if q.get('answerKey') else ''
        if not answer_key:
            errors.append(f"Question '{qid}' (multiple_choice) missing 'answerKey'.")
        elif choices and answer_key not in choices:
            errors.append(
                f"Question '{qid}' (multiple_choice) answerKey '{answer_key}' not found in choices."
            )
        if _has_mojibake(answer_key):
            errors.append(f"Question '{qid}' (multiple_choice) answerKey contains mojibake artifacts.")

    elif qtype == 'short_answer':
        answer_key = q.get('answerKey')
        if not answer_key.strip() if isinstance(answer_key, str) else not answer_key:
            errors.append(f"Question '{qid}' (short_answer) missing 'answerKey'.")
        if _has_mojibake(answer_key):
            errors.append(f"Question '{qid}' (short_answer) answerKey contains mojibake artifacts.")

    elif qtype == 'paragraph':
        if not q.get('prompt', '').strip():
            errors.append(f"Question '{qid}' (paragraph) missing 'prompt'.")

    elif qtype == 'audio_short_answer':
        if not q.get('audioText', '').strip():
            errors.append(f"Question '{qid}' (audio_short_answer) missing 'audioText'.")
        ak = q.get('answerKey')
        if not ak or (isinstance(ak, str) and not ak.strip()):
            errors.append(f"Question '{qid}' (audio_short_answer) missing 'answerKey'.")
        if _has_mojibake(q.get('audioText')) or _has_mojibake(ak):
            errors.append(f"Question '{qid}' (audio_short_answer) contains mojibake artifacts.")
        return 1

    return 0


def _extract_section_items(section: dict, sid: str, errors: list, warnings: list):
    items = section.get('items')
    questions = section.get('questions')

    if items is not None:
        if not isinstance(items, list):
            errors.append(f"Section '{sid}' 'items' must be a list.")
            return []
        if questions is not None:
            warnings.append(
                f"WARNING: Section '{sid}' includes both 'items' and legacy 'questions'. "
                f"Runtime will use 'items'."
            )
        return items

    if not isinstance(questions, list):
        errors.append(f"Section '{sid}' must include either 'items' or 'questions' as a list.")
        return []
    return questions


def _validate_stimulus_set_item(
    *,
    item: dict,
    sid: str,
    category: str,
    errors: list,
    warnings: list,
    question_ids: set,
    structured_math_enabled: bool,
) -> int:
    item_id = item.get('id', '').strip() if isinstance(item.get('id'), str) else '(unknown-stimulus-set)'

    if category not in STIMULUS_SET_ALLOWED_CATEGORIES:
        allowed = ', '.join(f"'{c}'" for c in sorted(STIMULUS_SET_ALLOWED_CATEGORIES))
        errors.append(
            f"Item '{item_id}' (stimulus_set) is not allowed in category '{category}'. "
            f"Allowed categories: {allowed}."
        )

    stimulus_format = item.get('stimulusFormat')
    if stimulus_format != 'text':
        errors.append(f"Item '{item_id}' (stimulus_set) must set stimulusFormat='text'.")

    stimulus_text = item.get('stimulusText')
    if not isinstance(stimulus_text, str) or not stimulus_text.strip():
        errors.append(f"Item '{item_id}' (stimulus_set) must include non-empty 'stimulusText'.")
    elif _has_mojibake(stimulus_text):
        errors.append(f"Item '{item_id}' (stimulus_set) stimulusText contains mojibake artifacts.")

    child_questions = item.get('questions')
    if not isinstance(child_questions, list):
        errors.append(f"Item '{item_id}' (stimulus_set) 'questions' must be a list.")
        return 0

    if len(child_questions) != 3:
        errors.append(f"Item '{item_id}' (stimulus_set) must contain exactly 3 child questions.")

    audio_count = 0
    for idx, child in enumerate(child_questions):
        audio_count += _validate_standard_question(
            q=child,
            sid=sid,
            position_label=f"stimulus_set '{item_id}' child question {idx + 1}",
            category=category,
            errors=errors,
            warnings=warnings,
            question_ids=question_ids,
            structured_math_enabled=structured_math_enabled,
            allowed_types=STIMULUS_CHILD_SUPPORTED_TYPES,
        )
    return audio_count


def _validate_decision_tree_item(*, item: dict, category: str, errors: list):
    item_id = item.get('id', '').strip() if isinstance(item.get('id'), str) else '(unknown-decision-tree)'

    if category != DECISION_TREE_ALLOWED_CATEGORY:
        errors.append(
            f"Item '{item_id}' (decision_tree) is only allowed in category "
            f"'{DECISION_TREE_ALLOWED_CATEGORY}'."
        )

    _validate_subcategory_and_skill(
        qid=item_id,
        category=category,
        subcategory_value=item.get('subcategory'),
        skill_value=item.get('skill'),
        errors=errors,
    )

    title = item.get('title')
    if not isinstance(title, str) or not title.strip():
        errors.append(f"Item '{item_id}' (decision_tree) missing non-empty 'title'.")

    entry_node_id = item.get('entryNodeId')
    if not isinstance(entry_node_id, str) or not entry_node_id.strip():
        errors.append(f"Item '{item_id}' (decision_tree) missing non-empty 'entryNodeId'.")

    nodes = item.get('nodes')
    if not isinstance(nodes, list) or len(nodes) == 0:
        errors.append(f"Item '{item_id}' (decision_tree) must include non-empty 'nodes'.")
        return

    node_ids = set()
    node_by_id = {}
    ending_count = 0
    edges = []

    for idx, node in enumerate(nodes):
        label = f"Item '{item_id}' node index {idx}"
        if not isinstance(node, dict):
            errors.append(f"{label} must be an object.")
            continue

        node_id = node.get('id')
        if not isinstance(node_id, str) or not node_id.strip():
            errors.append(f"{label} missing non-empty 'id'.")
            continue

        if node_id in node_ids:
            errors.append(f"Item '{item_id}' has duplicate node id '{node_id}'.")
            continue

        node_ids.add(node_id)
        node_by_id[node_id] = node

        node_type = node.get('nodeType')
        if node_type == 'choice':
            prompt = node.get('prompt')
            if not isinstance(prompt, str) or not prompt.strip():
                errors.append(f"Item '{item_id}' choice node '{node_id}' missing non-empty 'prompt'.")

            choices = node.get('choices')
            if not isinstance(choices, list) or len(choices) < 2:
                errors.append(f"Item '{item_id}' choice node '{node_id}' must include at least 2 choices.")
                continue

            choice_ids = set()
            for cidx, choice in enumerate(choices):
                clabel = f"Item '{item_id}' choice node '{node_id}' choice index {cidx}"
                if not isinstance(choice, dict):
                    errors.append(f"{clabel} must be an object.")
                    continue

                choice_id = choice.get('id')
                choice_label = choice.get('label')
                next_node_id = choice.get('nextNodeId')

                if not isinstance(choice_id, str) or not choice_id.strip():
                    errors.append(f"{clabel} missing non-empty 'id'.")
                elif choice_id in choice_ids:
                    errors.append(
                        f"Item '{item_id}' choice node '{node_id}' has duplicate choice id '{choice_id}'."
                    )
                else:
                    choice_ids.add(choice_id)

                if not isinstance(choice_label, str) or not choice_label.strip():
                    errors.append(f"{clabel} missing non-empty 'label'.")

                if not isinstance(next_node_id, str) or not next_node_id.strip():
                    errors.append(f"{clabel} missing non-empty 'nextNodeId'.")
                else:
                    edges.append((node_id, next_node_id))

        elif node_type == 'ending':
            ending_count += 1
            ending_title = node.get('title')
            conclusion = node.get('conclusion')
            if not isinstance(ending_title, str) or not ending_title.strip():
                errors.append(f"Item '{item_id}' ending node '{node_id}' missing non-empty 'title'.")
            if not isinstance(conclusion, str) or not conclusion.strip():
                errors.append(f"Item '{item_id}' ending node '{node_id}' missing non-empty 'conclusion'.")
            if node.get('choices') is not None:
                errors.append(f"Item '{item_id}' ending node '{node_id}' must not include 'choices'.")
        else:
            errors.append(
                f"Item '{item_id}' node '{node_id}' has unsupported nodeType '{node_type}'. "
                f"Use 'choice' or 'ending'."
            )

    if ending_count == 0:
        errors.append(f"Item '{item_id}' (decision_tree) must include at least one ending node.")

    if isinstance(entry_node_id, str) and entry_node_id.strip() and entry_node_id not in node_by_id:
        errors.append(
            f"Item '{item_id}' (decision_tree) entryNodeId '{entry_node_id}' does not reference a valid node."
        )

    for source_node_id, target_node_id in edges:
        if target_node_id not in node_by_id:
            errors.append(
                f"Item '{item_id}' choice from node '{source_node_id}' points to missing node '{target_node_id}'."
            )



def validate_authoring_quiz(quiz: dict) -> tuple:
    """
    Validate an authoring quiz dict.
    Returns (errors, warnings) where both are lists of strings.
    Errors are fatal; warnings are advisory.
    """
    errors = []
    warnings = []
    structured_math_enabled = os.getenv('QUIZ_ENABLE_STRUCTURED_MATH', '1').strip().lower() not in {'0', 'false', 'no', 'off'}

    if not isinstance(quiz, dict):
        errors.append("Quiz must be a JSON object (dict).")
        return errors, warnings

    # A. Required top-level fields
    for field in REQUIRED_TOP_LEVEL:
        if field not in quiz:
            errors.append(f"Missing required top-level field: '{field}'")
        elif quiz[field] in ('', None):
            errors.append(f"Top-level field '{field}' must not be empty.")

    # B. Taxonomy validation
    category = quiz.get('category', '')
    subcategory = quiz.get('subcategory', '')
    skill = quiz.get('skill', '')
    difficulty = quiz.get('difficulty_level')
    date_created = quiz.get('dateCreated', '')

    if category and category not in TAXONOMY:
        valid_cats = ', '.join(f"'{c}'" for c in TAXONOMY.keys())
        errors.append(f"Invalid 'category': '{category}'. Must be one of: {valid_cats}")
    # Legacy compatibility: allow top-level subcategory/skill metadata if present,
    # but taxonomy validation and generation are question-level under Option A.
    if subcategory or skill:
        warnings.append(
            "WARNING: Top-level 'subcategory'/'skill' are legacy metadata. "
            "Question-level taxonomy fields are authoritative."
        )

    if difficulty is not None:
        if not isinstance(difficulty, (int, float)) or not (6.0 <= difficulty <= 16.0):
            errors.append(f"'difficulty_level' must be a number between 6.0 and 16.0, got: {difficulty!r}")

    if not date_created:
        warnings.append("WARNING: 'dateCreated' missing; publish will auto-set the current date.")
    elif not DATE_RE.match(str(date_created)):
        errors.append(f"'dateCreated' must be in YYYY-MM-DD format, got: '{date_created}'")

    sections = quiz.get('sections')
    if sections is None:
        return errors, warnings

    if not isinstance(sections, list):
        errors.append("'sections' must be a list.")
        return errors, warnings

    if len(sections) == 0:
        errors.append("'sections' must not be empty.")
        return errors, warnings

    # C. Walk sections and items/questions
    section_ids: set = set()
    question_ids: set = set()
    item_ids: set = set()
    audio_count = 0

    for i, section in enumerate(sections):
        if not isinstance(section, dict):
            errors.append(f"Section {i + 1} is not an object.")
            continue

        sid = section.get('id', '').strip()
        if not sid:
            errors.append(f"Section {i + 1} missing 'id'.")
        elif sid in section_ids:
            errors.append(f"Duplicate section id: '{sid}'.")
        else:
            section_ids.add(sid)

        section_items = _extract_section_items(section, sid, errors, warnings)
        if len(section_items) == 0:
            warnings.append(f"WARNING: Section '{sid}' has no items/questions.")
            continue

        for j, item in enumerate(section_items):
            if not isinstance(item, dict):
                errors.append(f"Section '{sid}' item {j + 1} is not an object.")
                continue

            item_id = item.get('id', '').strip() if isinstance(item.get('id'), str) else ''
            item_type = item.get('type', '').strip() if isinstance(item.get('type'), str) else ''

            if not item_id:
                errors.append(f"Section '{sid}' item {j + 1} missing 'id'.")
            elif item_id in item_ids:
                errors.append(f"Duplicate item id: '{item_id}'.")
            else:
                item_ids.add(item_id)

            if not item_type:
                errors.append(f"Section '{sid}' item '{item_id}' missing 'type'.")
                continue

            if item_type == STIMULUS_SET_TYPE:
                audio_count += _validate_stimulus_set_item(
                    item=item,
                    sid=sid,
                    category=category,
                    errors=errors,
                    warnings=warnings,
                    question_ids=question_ids,
                    structured_math_enabled=structured_math_enabled,
                )
                continue

            if item_type == DECISION_TREE_TYPE:
                _validate_decision_tree_item(item=item, category=category, errors=errors)
                continue

            audio_count += _validate_standard_question(
                q=item,
                sid=sid,
                position_label=f"item {j + 1}",
                category=category,
                errors=errors,
                warnings=warnings,
                question_ids=question_ids,
                structured_math_enabled=structured_math_enabled,
            )

    # E. Build readiness info
    if audio_count > 0:
        warnings.append(
            f"INFO: {audio_count} audio_short_answer question(s) detected — "
            f"TTS media will be generated during Build and Publish."
        )

    return errors, warnings
