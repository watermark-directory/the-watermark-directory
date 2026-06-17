/**
 * End-use & workloads explorer (#251 interactive layer). The report's [verified]
 * taxonomy, made selectable: pick one of the four things called "data center" and
 * read who owns the compute, who benefits, and — the axis that narrows — who can
 * even use it. A persistent Lima readout holds the payoff: confirming the customer
 * (Google) did not resolve the use.
 *
 * Mounted `client:only` over the page's SSR table (no-JS readable). The data is the
 * build-time `EndUseData` (curated from the committee record); the island imports
 * only the type.
 */
import { useState } from "react";
import { ACCESS_LABEL, ACCESS_ORDER, type DcKey, type EndUseData } from "../../lib/endUse";

export default function EndUseExplorer({ data }: { data: EndUseData }): JSX.Element {
  const [activeKey, setActiveKey] = useState<DcKey>("hyperscale");
  const active = data.types.find((t) => t.key === activeKey) ?? data.types[0];
  const accessIndex = ACCESS_ORDER.indexOf(active.access as (typeof ACCESS_ORDER)[number]);

  return (
    <div
      className="eu"
      role="figure"
      aria-label="Interactive: the four businesses called 'data center' and what the Lima record says about each. The same content is in the table on this page."
    >
      <div className="eu-tabs" role="group" aria-label="Type of data center">
        {data.types.map((t) => (
          <button
            key={t.key}
            type="button"
            className={`eu-tab${t.key === activeKey ? " is-active" : ""}${
              t.limaStatus === "ruled-out" ? " is-ruled-out" : ""
            }`}
            aria-pressed={t.key === activeKey}
            onClick={() => setActiveKey(t.key)}
          >
            <span className="eu-tab-label">{t.label}</span>
            <span className="eu-tab-tag">{t.tagline}</span>
          </button>
        ))}
      </div>

      <div className="eu-detail" role="status" aria-live="polite">
        <div className="eu-detail-head">
          <h3 className="eu-detail-title">{active.label}</h3>
          <span className={`eu-lima eu-lima--${active.limaStatus}`}>
            {active.limaStatus === "ruled-out" ? "Lima: ruled out" : "Lima: [open]"}
          </span>
        </div>

        <dl className="eu-attrs">
          <div className="eu-attr">
            <dt>Who owns the compute</dt>
            <dd>{active.ownsCompute}</dd>
          </div>
          <div className="eu-attr">
            <dt>Who benefits</dt>
            <dd>{active.whoBenefits}</dd>
          </div>
          <div className="eu-attr">
            <dt>Who can use it</dt>
            <dd>{active.whoCanUse}</dd>
          </div>
          <div className="eu-attr">
            <dt>Local economy</dt>
            <dd>{active.localEconomy}</dd>
          </div>
        </dl>

        {/* The "who can use it" axis, narrowing broad → sealed. */}
        <div className="eu-access" aria-hidden="true">
          {ACCESS_ORDER.map((lvl, i) => (
            <span
              key={lvl}
              className={`eu-access-seg${i === accessIndex ? " is-on" : ""}${
                accessIndex >= 0 && i <= accessIndex ? " is-filled" : ""
              }`}
            >
              {ACCESS_LABEL[lvl]}
            </span>
          ))}
        </div>
        <p className="eu-access-note">
          Who can use it: <strong>{ACCESS_LABEL[active.access]}</strong>
          {active.access === "authorized-only"
            ? " — the access the record cannot rule out, or confirm, for Lima."
            : ""}
        </p>

        <p className="eu-evidence">
          <span className="eu-evidence-mark" aria-hidden="true">
            ⌖
          </span>{" "}
          <span className="td-tag td-tag--verified">[verified]</span> {active.evidence}
        </p>
        <p className="eu-lima-note">{active.limaNote}</p>
      </div>

      <div className="eu-readout">
        <div className="eu-readout-row">
          <span className="td-tag td-tag--verified">[verified]</span>
          <span>{data.verified}</span>
        </div>
        <div className="eu-readout-row">
          <span className="td-tag td-tag--open">[open]</span>
          <span>{data.openQuestion}</span>
        </div>
      </div>
    </div>
  );
}
