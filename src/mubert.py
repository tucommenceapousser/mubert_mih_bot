

######################################### mubert
from sentence_transformers import SentenceTransformer

import httpx
import json
import time

from utils import get_tags_for_prompts, get_mubert_tags_embeddings, get_pat

minilm = SentenceTransformer('all-MiniLM-L6-v2')
mubert_tags_embeddings = get_mubert_tags_embeddings(minilm)

def get_track_by_tags(tags, pat, duration, maxit=60, loop=False):
    if loop:
        mode = "loop"
    else:
        mode = "track"
    r = httpx.post('https://api-b2b.mubert.com/v2/RecordTrackTTM',
                   json={
                       "method": "RecordTrackTTM",
                       "params": {
                           "pat": pat,
                           "duration": duration,
                           "tags": tags,
                           "mode": mode
                       }
                   })

    rdata = json.loads(r.text)
    assert rdata['status'] == 1, rdata['error']['text']
    trackurl = rdata['data']['tasks'][0]['download_link']

    print('Generating track ', end='')
    for i in range(maxit):
        r = httpx.get(trackurl)
        if r.status_code == 200:
            return trackurl
        time.sleep(1)


def generate_track_by_prompt(email, prompt, duration, loop=False):
    try:
        pat = get_pat(email)
        _, tags = get_tags_for_prompts(minilm, mubert_tags_embeddings, [prompt, ])[0]
        return get_track_by_tags(tags, pat, int(duration), loop=loop), "Success", tags
    except Exception as e:
        return None, str(e), ""

######################################### mubert end

