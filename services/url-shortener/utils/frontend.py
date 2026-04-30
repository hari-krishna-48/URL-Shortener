from werkzeug.datastructures import Headers


def requests_html(headers: Headers):
    '''
    Return true if the `Accept` header contains `text/html` and has a higher
    quality value than `application/json`.
    '''
    accept = headers.get('Accept')
    if not accept:
        return False
    types = [part.strip() for part in accept.split(',')]
    split_types = [t.split(';q=') for t in types]
    types_with_quality = {
        split[0]: 1.0 if len(split) < 2 else float(split[1])
        for split in split_types
    }

    text_html = types_with_quality.get('text/html', 0)
    text_wildcard = types_with_quality.get('text/*', 0)
    application_json = types_with_quality.get('application/json', 0)
    application_wildcard = types_with_quality.get('application/*', 0)
    highest = max(text_html, text_wildcard, application_json, application_wildcard)

    if highest == application_json:
        return False
    elif highest == text_html:
        return True
    elif highest == application_wildcard:
        return False
    else:
        return True
