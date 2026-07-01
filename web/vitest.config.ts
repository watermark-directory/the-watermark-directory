import { getViteConfig } from "astro/config";
import { fileURLToPath } from "node:url";

export default getViteConfig({
  resolve: {
    alias: {
      "@fn": fileURLToPath(new URL("./functions", import.meta.url)),
    },
  },
});
