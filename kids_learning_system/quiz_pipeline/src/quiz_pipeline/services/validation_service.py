"""
validation_service.py
Authoring quiz validation — used by GUI and CLI.
Returns (errors: list[str], warnings: list[str])
"""
import re

SUPPORTED_TYPES = {'multiple_choice', 'short_answer', 'paragraph', 'audio_short_answer'}
REQUIRED_TOP_LEVEL = ['id', 'title', 'ageGroup', 'category', 'subcategory', 'skill', 'difficulty_level', 'dateCreated', 'sections']

# Canonical quiz taxonomy — category → subcategory → [skills]
TAXONOMY = {
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

DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def validate_authoring_quiz(quiz: dict) -> tuple:
    """
    Validate an authoring quiz dict.
    Returns (errors, warnings) where both are lists of strings.
    Errors are fatal; warnings are advisory.
    """
    errors = []
    warnings = []

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
    elif category and subcategory:
        valid_subcats = TAXONOMY.get(category, {})
        if subcategory not in valid_subcats:
            valid_list = ', '.join(f"'{s}'" for s in valid_subcats.keys())
            errors.append(f"Invalid 'subcategory': '{subcategory}' for category '{category}'. Must be one of: {valid_list}")
        elif skill:
            valid_skills = valid_subcats.get(subcategory, [])
            if skill not in valid_skills:
                valid_skill_list = ', '.join(f"'{s}'" for s in valid_skills)
                errors.append(f"Invalid 'skill': '{skill}' for subcategory '{subcategory}'. Must be one of: {valid_skill_list}")

    if difficulty is not None:
        if not isinstance(difficulty, (int, float)) or not (1 <= difficulty <= 10):
            errors.append(f"'difficulty_level' must be a number between 1 and 10, got: {difficulty!r}")

    if date_created and not DATE_RE.match(str(date_created)):
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

    # C. Walk sections and questions
    section_ids: set = set()
    question_ids: set = set()
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

        questions = section.get('questions', [])
        if not isinstance(questions, list):
            errors.append(f"Section '{sid}' 'questions' must be a list.")
            continue
        if len(questions) == 0:
            warnings.append(f"WARNING: Section '{sid}' has no questions.")
            continue

        for j, q in enumerate(questions):
            if not isinstance(q, dict):
                errors.append(f"Section '{sid}' question {j + 1} is not an object.")
                continue

            qid = q.get('id', '').strip()
            qtype = q.get('type', '').strip()

            if not qid:
                errors.append(f"Section '{sid}' question {j + 1} missing 'id'.")
            elif qid in question_ids:
                errors.append(f"Duplicate question id: '{qid}'.")
            else:
                question_ids.add(qid)

            if not qtype:
                errors.append(f"Question '{qid}' missing 'type'.")
                continue

            if qtype not in SUPPORTED_TYPES:
                warnings.append(f"WARNING: Question '{qid}' has unsupported type: '{qtype}'.")
                continue

            # D. Per-type validation
            if qtype == 'multiple_choice':
                choices = q.get('choices', [])
                if not isinstance(choices, list) or len(choices) < 2:
                    errors.append(f"Question '{qid}' (multiple_choice) must have at least 2 choices.")
                answer_key = q.get('answerKey', '').strip() if q.get('answerKey') else ''
                if not answer_key:
                    errors.append(f"Question '{qid}' (multiple_choice) missing 'answerKey'.")
                elif choices and answer_key not in choices:
                    errors.append(
                        f"Question '{qid}' (multiple_choice) answerKey '{answer_key}' not found in choices."
                    )

            elif qtype == 'short_answer':
                if not q.get('answerKey', '').strip() if isinstance(q.get('answerKey'), str) else not q.get('answerKey'):
                    errors.append(f"Question '{qid}' (short_answer) missing 'answerKey'.")

            elif qtype == 'paragraph':
                if not q.get('prompt', '').strip():
                    errors.append(f"Question '{qid}' (paragraph) missing 'prompt'.")

            elif qtype == 'audio_short_answer':
                audio_count += 1
                if not q.get('audioText', '').strip():
                    errors.append(f"Question '{qid}' (audio_short_answer) missing 'audioText'.")
                ak = q.get('answerKey')
                if not ak or (isinstance(ak, str) and not ak.strip()):
                    errors.append(f"Question '{qid}' (audio_short_answer) missing 'answerKey'.")

    # E. Build readiness info
    if audio_count > 0:
        warnings.append(
            f"INFO: {audio_count} audio_short_answer question(s) detected — "
            f"TTS media will be generated during Build and Publish."
        )

    return errors, warnings
