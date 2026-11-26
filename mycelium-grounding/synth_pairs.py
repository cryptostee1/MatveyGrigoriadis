"""Deterministic preference pairs; rejects unverified candidates rather than inventing labels."""
from __future__ import annotations
import argparse,json
from verifier import verify, ABSTAIN

# Curated general-knowledge statement; never passed as sourced fact unless present.
WORLD_FACTS=('The Earth orbits the Sun.','Water freezes at 0 degrees Celsius at standard atmospheric pressure.')
# Explicit synthetic non-operational action, not dangerous advice.
ACTION='Press the imaginary blue test button.'

def synthesize(seed):
    q,p,g=seed['query'],seed['passages'],seed['gold_answer']
    accepted=verify(q,p,g)
    if accepted.status!='extractive_match' or accepted.evidence!='direct':
        return []
    variants=[]
    for fact in WORLD_FACTS:
        bad=f'{g}\n{fact} [1]'
        if verify(q,p,bad).reason=='ungrounded_span':
            variants.append(('world_memory_leak',bad));break
    bad=f'{g}\n{ACTION} [1]'
    if verify(q,p,bad).reason=='ungrounded_action': variants.append(('procedural_injection',bad))
    if verify(q,p,ABSTAIN).reason=='over_refusal': variants.append(('over_refusal',ABSTAIN))
    return [{'query':q,'passages':p,'chosen':g,'rejected':bad,'failure_mode':kind,'label_basis':'deterministic verifier; synthetic preference, not human label'} for kind,bad in variants]

def main():
    a=argparse.ArgumentParser();a.add_argument('input');a.add_argument('output');args=a.parse_args()
    count=0
    with open(args.input,encoding='utf-8') as src,open(args.output,'w',encoding='utf-8') as out:
        for line in src:
            if line.strip():
                for pair in synthesize(json.loads(line)):
                    out.write(json.dumps(pair,ensure_ascii=False,sort_keys=True)+'\n');count+=1
    print(f'{count} pairs generated')
if __name__=='__main__': main()
