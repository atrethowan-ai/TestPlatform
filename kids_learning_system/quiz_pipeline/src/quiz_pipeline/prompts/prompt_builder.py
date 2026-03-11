def build_prompt(child_summary):
    child_id = child_summary.get('childId', 'unknown')
    quiz_id = child_summary.get('quizId', 'unknown')
    domain_stats = child_summary.get('domainStats', {})
    weak_domains = child_summary.get('weakDomains', [])

    summary_lines = [f"Child ID: {child_id}", f"Quiz ID: {quiz_id}", "", "Domain Performance:"]
    for domain, stats in domain_stats.items():
        summary_lines.append(f"- {domain}: {stats['correct']} correct / {stats['total']} total")

    summary_lines.append("")
    summary_lines.append("Recommended Focus Areas:")
    if weak_domains:
        for domain in weak_domains:
            summary_lines.append(f"- {domain}")
    else:
        summary_lines.append("- None (all domains mastered)")

    prompt = "\n".join(summary_lines)
    return prompt
