import { describe, expect, it } from "vitest";
import {
  type AskCitation,
  badgeKind,
  escapeHtml,
  renderAnswer,
  renderSources,
  searchingHint,
  withBasePath,
} from "./askRender";

const CITES: AskCitation[] = [
  {
    marker: 1,
    id: "records:opc",
    feed: "records",
    title: "Roundabouts OPC — summary",
    url: "/site/records/opc/",
    source: "data/documents/aedg/PRR-01-bundle.ocr.pdf",
    page: 318,
    source_kind: "document",
    verified: true,
  },
];

describe("escapeHtml", () => {
  it("neutralizes HTML in model/data text", () => {
    expect(escapeHtml('<img src=x onerror="alert(1)">')).toBe(
      "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;",
    );
  });
});

describe("withBasePath", () => {
  it("joins base + root-absolute path without doubling slashes", () => {
    expect(withBasePath("/network/american-sugar-creek-allen-co", "/site/records/opc/")).toBe(
      "/network/american-sugar-creek-allen-co/site/records/opc/",
    );
    expect(withBasePath("/", "/timeline")).toBe("/timeline");
  });
});

describe("renderAnswer", () => {
  it("resolves a [n] marker to a deep link into the bundle", () => {
    const html = renderAnswer("The roundabouts cost ~$1.2M [1].", CITES, "/");
    expect(html).toContain('<a href="/site/records/opc/"');
    expect(html).toContain("[1]</a>");
    expect(html).toContain(
      'title="Roundabouts OPC — summary — data/documents/aedg/PRR-01-bundle.ocr.pdf p.318"',
    );
  });

  it("flags an unresolved marker instead of dropping it", () => {
    const html = renderAnswer("Mystery [4].", CITES, "/");
    expect(html).toContain("ask-cite--unresolved");
    expect(html).toContain("[4]</sup>");
  });

  it("escapes HTML in the answer body", () => {
    expect(renderAnswer("<script>alert(1)</script>", [], "/")).not.toContain("<script>");
  });

  it("renders bullet lists and bold", () => {
    expect(renderAnswer("- one\n- two", [], "/")).toContain("<ul><li>one</li><li>two</li></ul>");
    expect(renderAnswer("**bold** claim", [], "/")).toContain("<strong>bold</strong>");
  });

  it("prefixes citation links with the site base", () => {
    expect(renderAnswer("x [1]", CITES, "/network/american-sugar-creek-allen-co")).toContain(
      'href="/network/american-sugar-creek-allen-co/site/records/opc/"',
    );
  });
});

describe("searchingHint", () => {
  it("pluralizes the record count (#331)", () => {
    expect(searchingHint(6)).toBe("Searching 6 records…");
    expect(searchingHint(1)).toBe("Searching 1 record…");
    expect(searchingHint(0)).toBe("Searching 0 records…");
  });
});

describe("badgeKind", () => {
  it("maps provenance to an evidence badge", () => {
    expect(badgeKind(CITES[0])).toBe("verified");
    expect(badgeKind({ ...CITES[0], verified: false, source_kind: "derived" })).toBe("open");
    expect(badgeKind({ ...CITES[0], verified: false, source_kind: "document" })).toBe("inference");
  });
});

describe("renderSources", () => {
  it("lists each cited source with its badge + deep link, empty when none", () => {
    expect(renderSources([], "/")).toBe("");
    const html = renderSources(CITES, "/");
    expect(html).toContain("Sources used");
    expect(html).toContain('href="/site/records/opc/"');
    expect(html).toContain("evidence-verified");
    expect(html).toContain("p.318");
  });
});
