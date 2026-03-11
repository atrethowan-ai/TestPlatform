from typing import Dict, Any

def summarise_attempts(attempt: Dict[str, Any], quiz: Dict[str, Any]) -> Dict[str, Any]:
    """Aggregate performance by domain and identify weak domains."""
    domain_stats = {}
    domain_questions = {}
    for section in quiz.get('sections', []):
        for q in section.get('questions', []):
            domain = q.get('domain', 'unknown')
            domain_questions[q['id']] = domain
            if domain not in domain_stats:
                domain_stats[domain] = {'correct': 0, 'incorrect': 0, 'total': 0}

    for resp in attempt.get('responses', []):
        qid = resp['questionId']
        domain = domain_questions.get(qid, 'unknown')
        domain_stats[domain]['total'] += 1
        if resp.get('isCorrect'):
            domain_stats[domain]['correct'] += 1
        else:
            domain_stats[domain]['incorrect'] += 1

    weak_domains = [d for d, stats in domain_stats.items() if stats['correct'] < stats['total']]

    summary = {
        'childId': attempt.get('childId'),
        'quizId': attempt.get('quizId'),
        'domainStats': domain_stats,
        'weakDomains': weak_domains,
    }
    return summary
