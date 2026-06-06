#!/usr/bin/env bash
# Re-derive the vendor/CMS/registration fields from the saved captures (html/ + whois/).
# Emits TSV: slug, generator, vendor_credit, vendor_link, registrar, created
set -uo pipefail
cd "$(dirname "$0")"
printf 'slug\tgenerator\tvendor_credit\tvendor_link\tregistrar\tcreated\n'
for f in html/*.html; do
  s=$(basename "$f" .html)
  gen=$(grep -ioE '<meta name="generator" content="[^"]*"' "$f" | head -1 | sed -E 's/.*content="([^"]*)".*/\1/' | cut -c1-40)
  cred=$(sed 's/<[^>]*>/ /g' "$f" | tr -s ' \t\n' ' ' \
     | grep -ioE '(website|site|developed|designed|powered|built|created|hosted) by[ :]*[A-Za-z0-9.,&!'\''-]+([ ][A-Za-z0-9.,&!'\''-]+){0,4}' \
     | grep -ivE 'powered by (wordpress|wix|squarespace|elementor|slider|wpbakery|onetap)' \
     | grep -iE 'anne decker|now marketing|corpcomm|munibit|eschoolview|finalsite|edlio|civicplus|revize|mcg|drupal|by ' \
     | sed -E 's/ powered by .*//I' | sort -u | head -1)
  link=$(grep -oiE 'https?://[a-z0-9.-]*(annedecker|nowmarketing|now-marketing|corpcomm|munibit|eschoolview|civicplus|finalsite|edlio|revize)[a-z0-9.-]*' "$f" | sort -u | head -1)
  reg=$(grep -iE '^[[:space:]]*Registrar:' "whois/$s.whois.txt" 2>/dev/null | head -1 | sed -E 's/.*Registrar:[[:space:]]*//; s/[[:space:]]+$//')
  cre=$(grep -iE 'Creation Date:|Created On:|created:' "whois/$s.whois.txt" 2>/dev/null | head -1 | sed -E 's/.*[Dd]ate:[[:space:]]*//; s/.*created:[[:space:]]*//I; s/T.*//')
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$s" "${gen:-}" "${cred:-}" "${link:-}" "${reg:-}" "${cre:-}"
done
