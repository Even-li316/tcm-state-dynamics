#!/usr/bin/env python3
"""Publish a new version of the TSIE preprint on Zenodo with the DOI-bearing PDF."""
import json, urllib.request, urllib.error

TOK = open('/home/ubuntu/.hermes/zenodo_token.txt').read().strip()
OLD = 24296398
PDF = '/home/ubuntu/work/tcm_opensource/paper/tsie_preprint.pdf'
NAME = 'tsie_preprint.pdf'


def call(method, url, data=None, raw=None):
    h = {'Authorization': f'Bearer {TOK}'}
    body = None
    if raw is not None:
        h['Content-Type'] = 'application/octet-stream'
        body = raw
    elif data is not None:
        h['Content-Type'] = 'application/json'
        body = json.dumps(data).encode()
    r = urllib.request.Request(url, method=method, headers=h, data=body)
    try:
        with urllib.request.urlopen(r, timeout=180) as resp:
            t = resp.read().decode()
            try:
                return resp.status, json.loads(t)
            except Exception:
                return resp.status, t
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:600]


def main():
    st, d = call('POST', f'https://zenodo.org/api/records/{OLD}/versions')
    print('new version draft', st)
    if st not in (200, 201):
        print(d); return
    rid = d['id']
    print('draft id', rid, '| doi', d.get('doi'))

    st, _ = call('POST', f'https://zenodo.org/api/records/{rid}/draft/files', [{'key': NAME}])
    print('init file', st)
    pdf = open(PDF, 'rb').read()
    st, _ = call('PUT', f'https://zenodo.org/api/records/{rid}/draft/files/{NAME}/content', raw=pdf)
    print('upload', st, len(pdf), 'bytes')
    st, _ = call('POST', f'https://zenodo.org/api/records/{rid}/draft/files/{NAME}/commit')
    print('commit', st)

    st, rec = call('GET', f'https://zenodo.org/api/records/{rid}/draft')
    files = rec.get('files') if isinstance(rec, dict) else None
    print('files in draft:', [(f['key'], f['size']) for f in files] if isinstance(files, list) else files)

    st, p = call('POST', f'https://zenodo.org/api/records/{rid}/draft/actions/publish')
    print('publish', st)
    if isinstance(p, dict):
        print('version DOI:', p.get('doi'))
        print('URL:', p.get('links', {}).get('self_html'))
        open('/tmp/zenodo_doi_v2.txt', 'w').write(f"{p.get('doi')}\t{p.get('links',{}).get('self_html')}")
    else:
        print(p)


if __name__ == '__main__':
    main()
