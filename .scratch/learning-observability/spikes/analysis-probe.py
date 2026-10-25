"""THROWAWAY: synthetic counterexamples for the observability design, not learner analysis.

Run with Python's standard library. Writes a numerical report beside this file.
No learner data, policy changes, fitted parameters or production integration.
"""
import itertools
import json
import math
from pathlib import Path


def wilson(successes, trials, z=1.959963984540054):
    """Illustration conditional on an independent binomial sampling model."""
    p = successes / trials
    denominator = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denominator
    radius = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denominator
    return [center - radius, center + radius]


def calculate():
    differences = [0.1, 0.2, 0.3, 0.4]
    observed = sum(differences) / len(differences)
    assignments = [sum(s * d for s, d in zip(signs, differences)) / len(differences)
                   for signs in itertools.product([-1, 1], repeat=len(differences))]
    extreme = sum(abs(x) >= abs(observed) - 1e-12 for x in assignments)
    # Count fair-coin paths exactly; stop counting a path after its first rejection.
    survivors = {0: 1}
    rejected_at_20 = 0
    for n in range(1, 21):
        advanced = {}
        for successes, paths in survivors.items():
            for s in (successes, successes + 1):
                advanced[s] = advanced.get(s, 0) + paths
        survivors = {}
        for s, paths in advanced.items():
            tail_twice = 2 * sum(math.comb(n, j) for j in range(min(s, n - s) + 1))
            if 20 * tail_twice <= 2 ** n:
                rejected_at_20 += paths * 2 ** (20 - n)
            else:
                survivors[s] = paths
    fixed_rejections = sum(math.comb(20, s) for s in range(21)
                           if 20 * 2 * sum(math.comb(20, j) for j in range(min(s, 20 - s) + 1)) <= 2 ** 20)
    return {
        'scope': 'All numbers authored. These are calculation/assumption probes, not learner results.',
        'missing_endpoint': {
            'success': 5, 'error': 2, 'missing': 1,
            'judged_success_fraction': 5 / 7, 'completion': 7 / 8,
            'possible_all_endpoint_success_fraction': [5 / 8, 6 / 8],
            'interpretation': 'Scenario bounds over this fixed set, not a confidence interval or imputation.'},
        'changing_mix': {
            'early': {'easy': [8, 10], 'hard': [18, 90], 'pooled': 26 / 100},
            'later': {'easy': [63, 90], 'hard': [1, 10], 'pooled': 64 / 100},
            'within_stratum_change': {'easy': -.1, 'hard': -.1},
            'interpretation': 'Pooled success rises while each stratum worsens. Show the separate strata and their denominators; no weighted utility score or causal adjustment is introduced.'},
        'duplicated_rows': {
            'distinct_episodes': {'success': 8, 'n': 10, 'conditional_wilson_95': wilson(8, 10)},
            'ten_copies_per_episode': {'success': 80, 'n': 100, 'invalid_wilson_95': wilson(80, 100)},
            'interpretation': 'Duplicated rows manufacture apparent precision. Even the 10-episode interval requires independent, comparable Bernoulli observations; ordinary adaptive learning history does not establish this.'},
        'matched_randomization': {
            'independent_randomized_pairs': 4, 'family_pair_differences': differences,
            'equal_pair_mean_difference': observed, 'assignments': assignments,
            'extreme_assignments_two_sided': extreme, 'exact_two_sided_p': extreme / len(assignments),
            'interpretation': 'Conditional calculation for randomized labels within independent matched family pairs, no interference, and a sharp no-effect null. Four favorable differences still give p=0.125. This is not evidence of no effect, an effect interval, a universal sample threshold, or an actual randomized study.'},
        'full_cost': {
            'A': {'answer_minutes': 12, 'other_minutes': 28, 'total_minutes': 40},
            'B': {'answer_minutes': 20, 'other_minutes': 12, 'total_minutes': 32},
            'partial_cost_prefers': 'A', 'full_cost_prefers': 'B',
            'interpretation': 'Cost ranking reverses. Efficiency superiority additionally requires comparable retained outcomes and acceptable trade-offs.'},
        'unplaced_cost': {
            'A_placed_minutes': 27, 'A_unplaced_minutes_possible': [0, 20], 'B_placed_minutes': 32,
            'A_possible_total_if_nonoverlapping': [27, 47],
            'interpretation': 'Scenario endpoints require the extra time to be nonoverlapping. Five extra minutes ties B; more reverses the preference. Unplaced time has no known probability distribution; conclusion unresolved.'},
        'paired_change': {
            'baseline_success': 2, 'baseline_error': 6, 'later_success': 5,
            'improved': 3, 'maintained': 2, 'persistent_gap': 2, 'missing_pair': 1,
            'interpretation': 'Five later successes are not five new capabilities. Neither the three changed outcomes nor the two maintained outcomes identify a causal learning effect.'},
        'repeated_peeking': {
            'model': '20 independent fair coin flips; two-sided exact binomial p <= .05',
            'all_20_flip_paths': 2 ** 20,
            'one_fixed_final_look': {'rejecting_paths': fixed_rejections, 'false_rejection_fraction': fixed_rejections / 2 ** 20},
            'look_after_every_flip': {'rejecting_paths': rejected_at_20, 'false_rejection_fraction': rejected_at_20 / 2 ** 20},
            'interpretation': 'Exact path counting under an invented null. Repeated fixed-sample tests raise the false-positive probability. This does not calibrate the actual learner data or choose a sequential method.'}
    }


if __name__ == '__main__':
    result = calculate()
    path = Path(__file__).with_name('analysis-results.json')
    path.write_text(json.dumps(result, indent=2) + '\n')
    print('Synthetic missing-result bound:', result['missing_endpoint']['possible_all_endpoint_success_fraction'])
    print('Mix reversal: pooled 26% -> 64%; both strata decline 10 percentage points.')
    print('Conditional Wilson intervals:', result['duplicated_rows'])
    print('Four-pair exact two-sided randomization p:', result['matched_randomization']['exact_two_sided_p'])
    print('Full-cost ranking reverses A -> B; unknown cost can make the result unresolved.')
    print('Wrote', path)
