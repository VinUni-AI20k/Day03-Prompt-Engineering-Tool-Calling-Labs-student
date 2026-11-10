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

Differs from `papers` (arXiv keyword search): `openalex` covers all venues, supports
author lookup and citation ranking.

Robustness: needs at least one of `query` / `author` (else error dict); `limit` coerced to
[1, 20]; unknown `sort` falls back to `cited`; unknown author returns empty `items` with
`note: "author not found"`; HTTP errors are returned as error dicts.
