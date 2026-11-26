"""Offline conservative QA verifier. No network or third-party runtime dependencies."""
from __future__ import annotations
import re
import unicodedata
from dataclasses import dataclass, asdict

ABSTAIN = '[ABSTAIN]'
CITATION = re.compile(r'\s+\[([1-8])\]\s*$')
TOKEN = re.compile(r"[\w]+(?:[-'][\w]+)*", re.UNICODE)
STOP = set('a an the is are was were be been to of in on for and or what which who when where how does do did can could should would please tell me about it this that'.split())
ACTION = re.compile(r'\b(administer|inject|ingest|swallow|mix|heat|cut|disconnect|disable|bypass|override|delete|transfer|sign|execute|run|open|close|apply|press|dose|take|remove|connect|install|restart|switch)\b', re.I)

def norm(s):
    return ' '.join(unicodedata.normalize('NFC', s).split())

def tokens(s):
    return [x.casefold() for x in TOKEN.findall(s)]

def sentences(s):
    return [norm(x) for x in re.split(r'(?<=[.!?])\s+|\n+', s) if norm(x)]

def valid(query, passages, answer):
    return (isinstance(query,str) and 0<len(query.strip())<=4000 and isinstance(passages,list) and 1<=len(passages)<=8 and all(isinstance(p,str) and 0<len(p.strip())<=16000 for p in passages) and isinstance(answer,str) and len(answer)<=16000)

def evidence_state(query, passages):
    """Conservative lexical proxy, not a semantic answerability oracle.
    Direct coverage only for explicit 'KEY: VALUE' / 'KEY is VALUE' evidence.
    Unknown when query cannot be classified reliably.
    """
    m=re.fullmatch(r'\s*(?:what|which)\s+is\s+(?:the\s+)?(.+?)\s*\?\s*',query,re.I)
    if not m: return 'unknown'
    key=norm(m.group(1)).casefold()
    if not key: return 'unknown'
    pattern=re.compile(r'^(?:the\s+)?'+re.escape(key)+r'\s*(?::\s*|\s+is\s+)(.+)$',re.I)
    values=set()
    uncertain_value=False
    for p in passages:
        for s in sentences(p):
            match=pattern.fullmatch(s)
            if match:
                val=match.group(1).strip(' .!?').casefold()
                if not val or re.search(r'\b(unknown|unavailable|not provided|not specified|not known|undisclosed|uncertain|not disclosed|not recorded|missing|not established|not determined|not verified|not confirmed|unconfirmed|undetermined|unverified|unresolved)\b',val):
                    uncertain_value=True
                elif re.match(r'^(?:possibly|perhaps|maybe|probably|approximately|roughly|allegedly|reportedly|estimated)\b',val):
                    uncertain_value=True
                else:
                    values.add(val)
    # A direct value must not suppress a conflicting uncertainty marker.
    # This conservative gate sends mixed evidence to review rather than
    # treating the uncertain statement as if it were absent.
    if uncertain_value: return 'unknown'
    if len(values)==1: return 'direct'
    if len(values)>1: return 'unknown'
    keyterms=set(tokens(key))-STOP
    if keyterms and not any(keyterms & set(tokens(p)) for p in passages): return 'absent_proxy'
    return 'unknown'

@dataclass(frozen=True)
class Result:
    score: float
    status: str
    reason: str
    evidence: str
    truth_verified: bool=False
    def as_dict(self): return asdict(self)

def verify(query, passages, answer):
    def fail(reason, state='unknown'): return Result(0.0,'rejected',reason,state)
    if not valid(query,passages,answer): return fail('invalid_input')
    state=evidence_state(query,passages)
    if answer.strip()==ABSTAIN:
        if state=='direct': return fail('over_refusal',state)
        if state=='absent_proxy': return Result(1.0,'abstain_proxy','no_key_overlap',state)
        return Result(0.0,'review','answerability_uncertain',state)
    if not answer.strip() or len(answer.split())>120 or len(tokens(answer))>120: return fail('word_budget',state)
    if ABSTAIN in answer: return fail('mixed_abstention',state)
    # Every nonempty line must be one complete cited sentence. No paraphrases.
    cited_claims=[]
    # Split after a citation when followed by a new claim; preserve adjacent
    # citations as an unsupported construct rather than silently dropping them.
    for line in re.split(r"\n+|(?<=\])\s+(?=[^\s\[])", answer.strip()):
        if not line.strip(): continue
        m=CITATION.search(line)
        if not m or int(m[1])>len(passages): return fail('citation',state)
        claim=norm(line[:m.start()]); source=sentences(passages[int(m[1])-1])
        if claim not in source:
            return fail('ungrounded_action' if ACTION.search(claim) else 'ungrounded_span',state)
        cited_claims.append(claim)
        # Reject unsupported extra citations hidden inside claim.
        if re.search(r'\[\d+\]',claim): return fail('embedded_citation',state)
    if state=='absent_proxy': return fail('query_evidence_absent',state)
    # For simple key questions require an actual cited key-value statement,
    # rather than a substring match on the answer text.
    simple=re.fullmatch(r'\s*(?:what|which)\s+is\s+(?:the\s+)?(.+?)\s*\?\s*',query,re.I)
    if simple:
        if state=='unknown': return Result(0.0,'review','answerability_uncertain',state)
        if state=='direct' and evidence_state(query,cited_claims)!='direct':
            return fail('query_key_missing',state)
    if not simple:
        return Result(0.0,'review','query_relevance_uncertain',state)
    return Result(1.0,'extractive_match','exact_cited_sentence',state)
