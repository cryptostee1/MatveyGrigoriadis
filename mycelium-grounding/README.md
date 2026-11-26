# MYCELIUM Grounding Toolkit v0.5 — research candidate

Public standalone candidate for [issue #6 / t=21](https://github.com/incidere/solana-agent-bounties/issues/6). AI-assisted implementation. No payout or acceptance confirmed. Only this component is published, not the private MYCELIUM/GMG core.

## Run offline

Python standard library at runtime; pytest must already be installed. From this folder, run `python -m pytest -q` and `python synth_pairs.py seeds.jsonl pairs.jsonl`.

Actual local execution on Python 3.13.5: 136 pytest cases passed (including 24 uncertainty regression cases). Python 3.12 grammar compatibility was checked previously; execution on 3.12 is not verified. Socket operations are blocked in test fixtures. No paid APIs.

The verifier accepts exact cited sentences with a single [1]–[8] citation, or [ABSTAIN]. It intentionally rejects paraphrases and many valid complex answers. Simple key-value questions use a conservative lexical answerability proxy. Conflicting or uncertain evidence and broader questions route to review. It does not establish factual truth, semantic entailment, general relevance, calibrated abstention, or safety of cited instructions. Do not deploy for high-stakes decisions. DPO preferences are synthetic, not human labels. The included demonstration seed yields three rejected examples. Full bounty compliance is not established.

## Payout address (Solana Mainnet, receive only)

`CdufeSmEtTQqY2N43jByeywnhWvDj2KQ7ztVS4np3r5E`

No keys, wallet connection, transactions or spending. No license grant beyond public inspection and evaluation is intended here.
