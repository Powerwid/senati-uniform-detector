import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@modules": path.resolve(__dirname, "./src/modules"),
      "@layouts": path.resolve(__dirname, "./src/modules/layouts"),
      "@detector": path.resolve(__dirname, "./src/modules/detector"),
      "@auth": path.resolve(__dirname, "./src/modules/auth"),
      "@common": path.resolve(__dirname, "./src/common"),
      "@pages": path.resolve(__dirname, "./src/pages"),
      "@images": path.resolve(__dirname, "./src/assets/images"),
      "@videos": path.resolve(__dirname, "./src/assets/videos")
    }
  }
});