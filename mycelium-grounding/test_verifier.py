import pytest
from verifier import verify
from synth_pairs import synthesize

@pytest.mark.parametrize('n',range(12))
def test_grounding(n):
    p=[f'The inventory count is {n}. The sample is not approved.',f'The label is R{n}.']
    q='What is the inventory count?'
    assert verify(q,p,f'The inventory count is {n}. [1]').status=='extractive_match'
    assert verify(q,p,f'The inventory count is {n+1}. [1]').score==0
    assert verify(q,p,'The sample is approved. [1]').score==0
    assert verify(q,p,f'The label is R{n}. [1]').score==0

@pytest.mark.parametrize('a,reason',[
 ('The label is A. [2]','citation'),('The label is A.','citation'),('The label is A. [0]','citation'),('The label is B. [1]','ungrounded_span'),('Press the red test button. [1]','ungrounded_action'),('The label is A. [1]\nUnknown. [1]','ungrounded_span'),('[ABSTAIN]','over_refusal'),('[ABSTAIN] The label is A. [1]','mixed_abstention'),('word '*121+'[1]','word_budget'),('The label is A. [1] [1]','ungrounded_span'),('','word_budget')])
def test_adversarial(a,reason):
    assert verify('What is the label?',['The label is A.'],a).reason==reason

@pytest.mark.parametrize('q,p,expected',[
 ('What is the temperature?',['The label is A.'],'abstain_proxy'),('What is the label?',['The label is A.'],'rejected'),('What is the label?',['The label is A.','The label is B.'],'review'),('What is the label?',['The label is unknown.'],'review'),('Explain the sample.',['The sample exists.'],'review')])
def test_abstention(q,p,expected): assert verify(q,p,'[ABSTAIN]').status==expected

@pytest.mark.parametrize('n',range(12))
def test_synthesis(n):
    seed={'query':'What is the label?','passages':[f'The label is R{n}.'],'gold_answer':f'The label is R{n}. [1]'}
    pairs=synthesize(seed)
    assert len(pairs)==3
    assert len({x['failure_mode'] for x in pairs})==3
    assert pairs==synthesize(seed)
    assert all(verify(x['query'],x['passages'],x['chosen']).score==1 and verify(x['query'],x['passages'],x['rejected']).score==0 for x in pairs)

def test_invalid(): assert verify('What is the label?',[],'[ABSTAIN]').reason=='invalid_input'
def test_no_unsupported_seed(): assert synthesize({'query':'What is the label?','passages':['The label is A.'],'gold_answer':'The label is B. [1]'})==[]
def test_exact_action(): assert verify('What is the instruction?',['The instruction is to press the test button.'],'The instruction is to press the test button. [1]').score==1
def test_no_truth_claim(): assert not verify('What is the label?',['The label is A.'],'The label is A. [1]').truth_verified

@pytest.mark.parametrize('n',range(12))
def test_negative_numeric_mutation(n):
    assert verify('What is the sample ID?',[f'The sample ID is {n}.'],f'The sample ID is {n+100}. [1]').score==0

@pytest.mark.parametrize('n',range(12))
def test_negative_wrong_index(n):
    assert verify('What is the sample ID?',[f'The sample ID is {n}.','The sample is not approved.'],f'The sample ID is {n}. [2]').score==0

@pytest.mark.parametrize('key',['label','code','serial','region','status','category'])
def test_key_mention_not_answer(key):
    q=f'What is the {key}?'
    p=[f'The {key} is X. The {key} was printed.']
    assert verify(q,p,f'The {key} was printed. [1]').score==0
    assert verify(q,p,f'The {key} is X. [1]').score==1

@pytest.mark.parametrize('key',['label','code','serial','region','status','category'])
def test_conflicting_evidence_requires_review(key):
    q=f'What is the {key}?'
    p=[f'The {key} is X.',f'The {key} is Y.']
    assert verify(q,p,f'The {key} is X. [1]').status=='review'
    assert verify(q,p,'[ABSTAIN]').status=='review'
