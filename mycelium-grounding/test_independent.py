"""New adversarial test families, not copied from the v0.3 suite."""
import pytest
from verifier import verify
from synth_pairs import synthesize

@pytest.mark.parametrize('q',['Explain why the project failed.','How does the relay work?','Who approved the package?','When was the report released?','Is the label valid?','Compare the two samples.','Summarize the evidence.','What happened yesterday?'])
def test_unknown_query_relevance(q):
    r=verify(q,['The label is A.'],'The label is A. [1]')
    assert r.status=='review' and r.score==0

@pytest.mark.parametrize('key',['lot','model','revision','batch','zone','group','tag','class'])
def test_inline_multiple_claims(key):
    q=f'What is the {key}?'
    p=[f'The {key} is C.','The sample is archived.']
    a=f'The {key} is C. [1] The sample is archived. [2]'
    assert verify(q,p,a).score==1
    assert verify(q,p,a+' An unrelated claim.').score==0
    assert verify(q,p,a.replace('archived','approved')).score==0
    assert verify(q,p,a.replace('[2]','[3]')).score==0

@pytest.mark.parametrize('key',['asset','revision','unit','owner','period','currency','sample','code'])
def test_uncertainty_conflict_and_abstention(key):
    q=f'What is the {key}?'
    known=[f'The {key} is R.']; unknown=['The unrelated marker is K.']; conflict=known+[f'The {key} is S.']
    assert verify(q,known,'[ABSTAIN]').reason=='over_refusal'
    assert verify(q,unknown,'[ABSTAIN]').status=='abstain_proxy'
    assert verify(q,conflict,'[ABSTAIN]').status=='review'
    assert verify(q,conflict,f'The {key} is R. [1]').score==0

@pytest.mark.parametrize('i',range(8))
def test_preference_no_mislabeled_unknown(i):
    assert synthesize({'query':f'How was sample {i} created?','passages':[f'The label is Q{i}.'],'gold_answer':f'The label is Q{i}. [1]'})==[]
