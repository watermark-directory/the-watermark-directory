#!/usr/bin/env bash
# Capture original web records for the Allen County, OH government-entity vendor audit.
# Input: lines of "slug|Entity Name|url" on stdin (|-separated).
# For each: saves raw HTML, runs whois on the registrable domain, and emits a
# TSV finding row (slug, http_status, vendor/credit signal, CMS generator, domain, registrar).
# Idempotent: re-running overwrites the per-entity capture. Never edits data/extracted.
set -uo pipefail
cd "$(dirname "$0")"
UA="Mozilla/5.0 (compatible; public-records-audit/1.0; Allen County OH government website vendor audit)"
mkdir -p html whois

printf 'slug\tstatus\tcredit_signal\tcms_generator\tdomain\tregistrar\n'
while IFS='|' read -r slug name url; do
  [ -z "${slug:-}" ] && continue
  case "$slug" in \#*) continue;; esac
  # registrable domain (strip scheme, path, then take last 2 labels; keep 3 for .oh.us / .ohio.gov)
  host=$(printf '%s' "$url" | sed -E 's#^https?://##; s#/.*$##')
  case "$host" in
    *.oh.us|*.ohio.gov|*.state.oh.us) domain=$(printf '%s' "$host" | awk -F. '{n=NF; print $(n-2)"."$(n-1)"."$n}');;
    *) domain=$(printf '%s' "$host" | awk -F. '{n=NF; print $(n-1)"."$n}');;
  esac
  # fetch raw HTML
  body=$(curl -sL --max-time 30 --compressed -A "$UA" -w '\n__HTTP_STATUS__%{http_code}' "$url" 2>/dev/null)
  status=$(printf '%s' "$body" | grep -o '__HTTP_STATUS__[0-9]*' | tail -1 | sed 's/__HTTP_STATUS__//')
  html=$(printf '%s' "$body" | sed 's/__HTTP_STATUS__[0-9]*$//')
  printf '%s' "$html" > "html/${slug}.html"
  # credit signal: footer "designed/developed/powered/website/built by ..." + known local vendors
  credit=$(printf '%s' "$html" | grep -ioE '(designed|developed|powered|website|built|hosted|maintained|site)[[:space:]]+by[[:space:]:]*[^<>"]{0,70}|anne[[:space:]]?decker[^<>"]{0,40}|corpcomm[^<>"]{0,40}|civicplus|govoffice|revize|granicus|squarespace|wix\.com|weebly|godaddy website|duda' | sed -E 's/[[:space:]]+/ /g' | sort -u | head -3 | paste -sd' ; ' -)
  cms=$(printf '%s' "$html" | grep -ioE '<meta name="generator" content="[^"]*"' | head -1 | sed -E 's/.*content="([^"]*)".*/\1/')
  # whois
  who=$(whois "$domain" 2>/dev/null)
  printf '%s' "$who" > "whois/${slug}.whois.txt"
  registrar=$(printf '%s' "$who" | grep -iE '^[[:space:]]*Registrar:' | head -1 | sed -E 's/.*Registrar:[[:space:]]*//; s/[[:space:]]+$//')
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$slug" "${status:-ERR}" "${credit:-}" "${cms:-}" "$domain" "${registrar:-}"
done
