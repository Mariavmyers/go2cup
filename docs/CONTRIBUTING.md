# Contributing (Go2Cup)
- Files: /data for JSON, /docs for docs.
- JSON rules: 2-space indent, sorted keys, no comments, newline at end.
- City fields: id, name, country, region, lat, lng, heroImageUrl, tags[]
- Stadium fields: id, name, cityId, capacity, images[]
- Do not delete fields; deprecate with "status":"deprecated".
- Commit style: Conventional Commits (feat(data): add {city})
- PR must tick checklist in the PR template below.
