import { describe, expect, it } from "vitest";
import { buildLens, LENS_ORDER, lensCount, lensDatum } from "./directory";
import { SITES } from "./sites";

const LIMA_COUNTS = { docs: "2,140", records: "318" };

describe("directory lenses — one network, read three ways (#308)", () => {
  it("orders the lenses water → defense → surveillance (water is the live default)", () => {
    expect(LENS_ORDER).toEqual(["water", "defense", "surveillance"]);
  });

  it("water lens groups all 32 sites by basin, nested under the two divides", () => {
    const v = buildLens("water", LIMA_COUNTS);
    expect(v.groups).toHaveLength(9); // nine basins
    const total = v.groups.reduce((n, g) => n + g.rows.length, 0);
    expect(total).toBe(SITES.length);
    // Exactly two groups open a divide banner (Lake Erie, Ohio River), in drainage order.
    const divides = v.groups.filter((g) => g.divide).map((g) => g.divide?.label);
    expect(divides).toEqual(["Lake Erie drainage", "Ohio River drainage"]);
    // Lake Erie drains first: Maumee leads, the Ohio-River basins follow.
    expect(v.groups.map((g) => g.label)).toEqual([
      "Maumee",
      "Sandusky",
      "Cuyahoga",
      "Great Miami",
      "Little Miami",
      "Scioto",
      "Muskingum",
      "Mahoning",
      "Hocking",
    ]);
  });

  it("water lens shows Lima's real counts and a dash everywhere else — never a fabricated number", () => {
    const v = buildLens("water", LIMA_COUNTS);
    const rows = v.groups.flatMap((g) => g.rows);
    const lima = rows.find((r) => r.slug === "lima");
    // cols: site, watershed, phase, documents, records, facility
    expect(lima?.cells[3].text).toBe("2,140");
    expect(lima?.cells[4].text).toBe("318");
    for (const r of rows) {
      if (r.slug === "lima") continue;
      expect(r.cells[3].text).toBe("—");
      expect(r.cells[4].text).toBe("—");
      expect(r.cells[3].muted).toBe(true);
    }
  });

  it("defense lens groups assessed sites and sweeps the rest into a 'not yet assessed' chip tail", () => {
    const v = buildLens("defense", LIMA_COUNTS);
    const rowGroups = v.groups.filter((g) => g.kind === "rows");
    const chipGroups = v.groups.filter((g) => g.kind === "chips");
    expect(rowGroups.map((g) => [g.abbr, g.count])).toEqual([
      ["MIL", 3], // Lima, Springfield, WPAFB
      ["FED", 2], // New Albany, Columbus
      ["SUP", 1], // Lordstown
    ]);
    expect(chipGroups).toHaveLength(1);
    expect(chipGroups[0].count).toBe(SITES.length - 6);
    // No site is dropped: rows + chips cover the whole network.
    const covered = rowGroups.reduce((n, g) => n + g.rows.length, 0) + chipGroups[0].chips.length;
    expect(covered).toBe(SITES.length);
  });

  it("surveillance lens splits on-record from signal-only, with the rest in the chip tail", () => {
    const v = buildLens("surveillance", LIMA_COUNTS);
    const rowGroups = v.groups.filter((g) => g.kind === "rows");
    expect(rowGroups.map((g) => [g.abbr, g.count])).toEqual([
      ["OPR", 2], // Lima, New Albany
      ["SUB", 2], // Hamilton·Middletown, Columbus
    ]);
    const chips = v.groups.find((g) => g.kind === "chips");
    expect(chips?.count).toBe(SITES.length - 4);
  });

  it("counts assessment progress in the lens-card line, and the network in the water line", () => {
    expect(lensCount("water")).toBe("32 sites · 9 basins");
    expect(lensCount("defense")).toBe("6 assessed · 26 to review");
    expect(lensCount("surveillance")).toBe("4 assessed · 28 to review");
  });

  it("defaults an unassessed site to 'watch' under both theses — a dash, not a verdict", () => {
    const d = lensDatum("toledo");
    expect(d.def.group).toBe("watch");
    expect(d.def.nexus).toBe("—");
    expect(d.surv.group).toBe("watch");
    // Lima is the worked anchor under both.
    expect(lensDatum("lima").def.signal).toBe("anchor");
    expect(lensDatum("lima").surv.group).toBe("onrecord");
  });
});
