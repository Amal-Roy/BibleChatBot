import re
import requests
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest

def parse_reference(ref_str):
    ref_str = re.sub(r'\s+', ' ', ref_str.strip())
    m = re.match(r'^(.+?)\s+(\d+):(\d+)(?:\s*-\s*(\d+))?$', ref_str)
    if not m:
        return None
    return {
        'book': m.group(1).strip(),
        'chapter': m.group(2),
        'start_verse': m.group(3),
        'end_verse': m.group(4) or m.group(3)
    }

def fetch_from_bible_api(book, chapter, start_verse, end_verse):
    verse_range = f"{chapter}:{start_verse}"
    if end_verse and end_verse != start_verse:
        verse_range = f"{chapter}:{start_verse}-{end_verse}"
    query = f"{book} {verse_range}"
    url = "https://bible-api.com/" + requests.utils.quote(query, safe='')
    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            return resp.json()
        return {'error': f'Bible API returned status {resp.status_code}'}
    except requests.RequestException as e:
        return {'error': str(e)}

def chartboard(request):
    return render(request, 'bible_app/chartboard.html')

def get_verse_api(request):
    if request.method != 'GET':
        return HttpResponseBadRequest("Only GET allowed")
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'success': False, 'error': 'No query provided'})
    parsed = parse_reference(q)
    if not parsed:
        return JsonResponse({'success': False, 'error': 'Could not parse reference. Use: John 3:16 or Psalm 23:1-3'})
    api_resp = fetch_from_bible_api(parsed['book'], parsed['chapter'], parsed['start_verse'], parsed['end_verse'])
    if 'error' in api_resp:
        return JsonResponse({'success': False, 'error': api_resp['error']})
    if 'verses' in api_resp:
        verses_text = "\n".join([f"{v.get('book_name')} {v.get('chapter')}:{v.get('verse')}. {v.get('text').strip()}" for v in api_resp['verses']])
    else:
        verses_text = api_resp.get('text','')
    return JsonResponse({'success': True, 'data': {'reference': q, 'text': verses_text, 'ai_summary': None}})
