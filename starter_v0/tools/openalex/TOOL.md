---
name: openalex
track: bonus
kind: live_api
provider: OpenAlex (api.openalex.org)
requires_env: []
inputs: [query, author, sort, limit]
outputs: [items]
side_effect: false
---
# openalex

Finds scholarly papers by **author name** and/or **topic** using the public OpenAlex API
(no key). With `author`, the name is first resolved to an OpenAlex author id
(`/authors?search=`), then works are filtered by that id (`/works?filter=author.id:`).
With `query`, titles/abstracts are searched. Both can be combined
(e.g. author "Geoffrey Hinton" + topic "capsule").

`sort`: `cited` (most cited, default) or `recent` (newest). Each item has title, DOI/URL,
venue, year, citation count and the first three authors.

Boundaries: `openalex` is for **author-centred** search; topic-only rankings over a time
window ("top papers on X in the last 9 months") belong to `top_papers`; arXiv keyword
search is `papers`.

Robustness: needs at least one of `query` / `author` (else error dict); `limit` coerced to
[1, 20]; unknown `sort` falls back to `cited`; unknown author returns empty `items` with
`note: "author not found"`; HTTP errors are returned as error dicts.
