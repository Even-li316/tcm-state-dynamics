#!/usr/bin/env python3
import json, urllib.request

TOK = open('/home/ubuntu/.hermes/zenodo_token.txt').read().strip()
RID = 24296398


def req(method, url, data=None):
    h = {'Authorization': f'Bearer {TOK}', 'Content-Type': 'application/json'}
    r = urllib.request.Request(url, method=method, headers=h,
                               data=json.dumps(data).encode() if data is not None else None)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            t = resp.read().decode()
            try:
                return resp.status, json.loads(t)
            except Exception:
                return resp.status, t
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:600]


st, d = req('GET', f'https://zenodo.org/api/records/{RID}/draft')
print('draft', st, type(d).__name__)
if isinstance(d, dict):
    files = d.get('files', {})
    print('files block type:', type(files).__name__, list(files)[:5] if isinstance(files, dict) else files)
    ents = files.get('entries') if isinstance(files, dict) else None
    if isinstance(ents, list):
        for e in ents:
            print('  entry:', e.get('key'), e.get('size'), e.get('status'))
    print('title:', d.get('metadata', {}).get('title', '')[:70])

st, p = req('POST', f'https://zenodo.org/api/records/{RID}/draft/actions/publish')
print('publish', st)
if isinstance(p, dict):
    print('DOI:', p.get('doi'))
    print('URL:', p.get('links', {}).get('self_html'))
    open('/tmp/zenodo_doi.txt', 'w').write(str(p.get('doi')))
else:
    print(p)
