# `data/documents/lima/council/` — the City of Lima legislative record

The City of Lima's **instrument** shelf: council agendas, packets and the ordinance texts they
carry, acquired from the city's live agenda portal. Extractions mirror it at
`data/extracted/lima/council/`.

## Why this directory exists beside `lima/meetings/`

`data/documents/lima/meetings/` is **not** a general meeting shelf — it is the civic loader's
managed subtree for the body slug `lima` under the reference build's flat layout
(`watermark.civic.layout.meetings_dir`). Its depth is asserted, its contents are enumerated by a
`download-manifest.yaml` + `meeting-index.yaml` pair, and every file in it was placed there by
`watermark subdivisions download`. Hand-dropping files into it makes the manifest wrong without
the loader ever having run.

It is also a shelf for a **route that has stopped producing**. Everything under `meetings/` came
from the CivicPlus Agenda Center at `https://www.limaohio.gov/AgendaCenter/ViewFile/…`, whose
**City Council category ends at 2024-05-06** — `POST /AgendaCenter/UpdateCategoryList` with
`catID=1` offers only 2024, 2023, 2022 and older, and the three 2026 documents the index does
carry belong to the Board of Building and Appeals, the Land Bank Committee and the Traffic
Commission. The city labels that page "Archived Meeting Agendas & Minutes (Prior to May 2024)".

The live route is a different vendor: **PrimeGov** at `https://limaoh.primegov.com/`, embedded as
an iframe on `https://www.limaohio.gov/887/Agendas-Minutes`. So this shelf holds the PrimeGov-era
record, `meetings/` holds the Agenda Center-era record, and the boundary between them is a fact
about the city's publishing, not an accident of filing. Merging the two would bury it.

## Acquisition route (open, scriptable, no session)

- Meeting list: `GET https://limaoh.primegov.com/api/v2/PublicPortal/ListArchivedMeetings?year=YYYY`
  and `…/ListUpcomingMeetings` — JSON, one object per meeting, each with a `documentList` of
  `{id, templateName, publishDate}` (`Agenda` / `Packet` / `HTML Packet` / `Minutes`).
- Document bytes: `GET https://limaoh.primegov.com/Public/CompiledDocument/<documentList id>` —
  `application/pdf`, with the as-received name in `Content-Disposition`.
- ⚠️ `Portal/MeetingPreview?compiledMeetingDocumentFileId=<id>`, which is what the portal's own JS
  links, **requires a login**. `Public/CompiledDocument/<id>` does not. Use the latter.
- The city's `/915/Public-Records-Search` returns HTTP 403 to automated requests, and American
  Legal's Lima code library (`codelibrary.amlegal.com`) is behind a Cloudflare interstitial. A
  moratorium ordinance is uncodified in any case, so neither is the route to this instrument.

## Naming

Source files keep their **as-received** names — here PrimeGov's own
`Meetings<meetingId><Template>_<YYYYMMDDHHMMSSmmm>.pdf`, taken from `Content-Disposition`. The
indexer-friendly name is recorded in `filename-map.yaml` as `canonical` and never imposed on the
file. `content_verified` records how the meeting date was established from the document's own
bytes — never from the filename, the API's `dateTime` field, or news coverage.
