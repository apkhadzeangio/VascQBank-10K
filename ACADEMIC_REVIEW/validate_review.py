"""Validate an academic checkpoint without modifying source or review files.

Usage: python ACADEMIC_REVIEW/validate_review.py
Optional --overlay-json accepts a resolved GitHub source snapshot for a local
read-only working copy older than the reviewed remote commit.
"""
import argparse
import collections
import hashlib
import json
import re
import unicodedata
from pathlib import Path

def normalize(text):
    return '\n'.join(line.rstrip() for line in unicodedata.normalize('NFC',text.replace('\r\n','\n').replace('\r','\n')).strip().split('\n'))

def records(text):
    hits=list(re.finditer(r'(?m)^(\d+)\.\s',text))
    return [(int(m[1]),text[m.start():hits[i+1].start() if i+1<len(hits) else len(text)].strip()) for i,m in enumerate(hits)]

def validate(directory,overlay=None):
    directory=Path(directory);root=directory.parent
    state=json.loads((directory/'REFINEMENT_STATE.json').read_text())
    entries=state['entries'];reviewed=json.loads((directory/'REFINED_RECORDS.json').read_text())
    evidence=json.loads((directory/'EVIDENCE_REGISTRY.json').read_text())['sources']
    master=(directory/'REFINED_MASTER_QBANK.txt').read_text()
    audit=[json.loads(l) for l in (directory/'REFINEMENT_AUDIT.jsonl').read_text().splitlines() if l]
    issues=[json.loads(l) for l in (directory/'REFINEMENT_ISSUES.jsonl').read_text().splitlines() if l]
    overlay=overlay or {}
    source_text={}
    for path,meta in state['source_files'].items():
        data=overlay[path]['content'].encode() if path in overlay else (root/path).read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        assert blob==meta['sha'],('source_blob_changed',path)
        source_text[path]=data.decode('utf-8-sig')
    keys=set()
    for path,text in source_text.items():
        if not path.endswith('_questions.txt'):continue
        topic=path.removesuffix('_questions.txt')
        qs=records(text);es=records(source_text[topic+'_explanations.txt'])
        assert [i for i,_ in qs]==list(range(1,len(qs)+1)),path
        assert [i for i,_ in qs]==[i for i,_ in es],path
        for (qid,q),(_,e) in zip(qs,es,strict=True):
            key=f'{topic}:{qid}';assert key not in keys;keys.add(key)
            opts=re.findall(r'(?m)^(\*?)([აბგდე])\)\s*(.*)$',q)
            assert [a for _,a,_ in opts]==list('აბგდე'),key
            correct=[a for star,a,_ in opts if star]
            assert len(correct)==1 and q.count('*')==1,key
            assert re.match(r'\d+\.\s*([აბგდე])\)',e)[1]==correct[0],key
            payload=json.dumps({'question':normalize(q),'explanation':normalize(e)},ensure_ascii=False,sort_keys=True,separators=(',',':'))
            assert hashlib.sha256(payload.encode()).hexdigest()==entries[key]['source_fingerprint'],key
    assert keys==set(entries)
    approved={k for k,v in entries.items() if v['review_status']=='APPROVED'}
    assert approved=={r['source_key'] for r in reviewed}
    assert len(reviewed)==len(approved)
    blocks=master.split('-'*50)[1:]
    master_keys=set()
    for block in blocks:
        topic=re.search(r'(?m)^TOPIC: (.+)$',block)[1]
        qid=int(re.search(r'(?m)^ORIGINAL ID: (\d+)$',block)[1])
        key=f'{topic}:{qid}';assert key not in master_keys;master_keys.add(key)
        fp=re.search(r'(?m)^SOURCE FINGERPRINT: ([a-f0-9]{64})$',block)[1]
        assert fp==entries[key]['reviewed_fingerprint']==entries[key]['source_fingerprint']
        opts=block.split('OPTIONS:\n',1)[1].split('\n\nCORRECT ANSWER:',1)[0]
        assert len(re.findall(r'(?m)^\*?[აბგდე]\)',opts))==5
        assert opts.count('*')==1
        answer=re.search(r'CORRECT ANSWER:\n([აბგდე])\)',block)[1]
        assert f'*{answer})' in opts
        for label in ['ACADEMIC EXPLANATION','CLINICAL REASONING','DISTRACTOR ANALYSIS','EVIDENCE','CLINICAL PEARL']:
            assert re.search(label+r':\n\S',block),(key,label)
    assert master_keys==approved
    assert f'Approved Total: {len(approved)}\n' in master
    for row in reviewed:
        assert all(row['qa_gates'].values()) and 90<=row['qa_score']<100
        assert row['correct_answer_text']==row['options'][row['correct_answer']]
        assert set(re.findall(r'([აბგდე])\)',row['distractor_analysis']))==set('აბგდე')-{row['correct_answer']}
        assert all(e in evidence and evidence[e]['verified_at'] for e in row['evidence_ids'])
    assert len({r['semantic_objective'] for r in reviewed})==len(reviewed)
    attempted={k for k,v in entries.items() if v['review_status']!='NEW'}
    assert attempted=={a['source_key'] for a in audit}
    assert len(audit)==len(attempted)
    assert {i['source_key'] for i in issues}==attempted-approved
    assert all(i['reason'] and i['remedy'] for i in issues)
    statuses=collections.Counter(r['review_status'] for r in entries.values())
    assert state['summary']['source_total']==len(keys)
    assert state['summary']['reviewed_total']==len(attempted)
    assert state['summary']['approved_total']==len(approved)
    assert state['summary']['pending_total']==len(issues)
    assert state['summary']['unreviewed_total']==statuses['NEW']
    result={'validation':'PASS','source_total':len(keys),'reviewed':len(attempted),'approved':len(approved),'pending':len(issues),'unreviewed':statuses['NEW'],'source_files_verified':len(source_text),'source_commit':state['source_commit_sha'],'duplicate_master_keys':0,'original_source_files_modified':False}
    print(json.dumps(result,ensure_ascii=False))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--overlay-json')
    args=parser.parse_args()
    overlay=json.loads(Path(args.overlay_json).read_text())['files'] if args.overlay_json else None
    validate(Path(__file__).resolve().parent,overlay)
