"""Regression: uncertainty markers cannot silently disappear from the evidence state."""
import pytest
from verifier import verify
from synth_pairs import synthesize

@pytest.mark.parametrize('marker',[
    'unknown','not provided','not confirmed','not verified','unconfirmed',
    'undetermined','possibly B','maybe B','estimated at 3','unresolved',
    'not established','not determined'])
def test_uncertainty_mixed_with_known(marker):
    q='What is the label?'
    p=['The label is A.',f'The label is {marker}.']
    for ans in ('The label is A. [1]',f'The label is A. [1]\nThe label is {marker}. [2]','[ABSTAIN]'):
        r=verify(q,p,ans)
        assert r.status=='review' and r.score==0
    assert synthesize({'query':q,'passages':p,'gold_answer':'The label is A. [1]'})==[]

@pytest.mark.parametrize('marker',['unknown','not verified','perhaps C','unresolved'])
def test_only_uncertain(marker):
    r=verify('What is the code?',[f'The code is {marker}.'],'[ABSTAIN]')
    assert r.status=='review' and r.score==0

@pytest.mark.parametrize('n',range(8))
def test_matching_duplicate_values_remain_direct(n):
    s=f'The code is R{n}.'
    r=verify('What is the code?',[s,s],s+' [2]')
    assert r.status=='extractive_match' and r.score==1
