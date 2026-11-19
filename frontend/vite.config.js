import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { parse } from 'smol-toml'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const configPath = path.resolve(__dirname, '../config.toml')

let apiHost = ''
let apiPort = 8000

if (fs.existsSync(configPath)) {
  const raw = fs.readFileSync(configPath, 'utf-8')
  const parsed = parse(raw)
  apiHost = parsed.server?.api_host || ''
  apiPort = parsed.server?.port || 8000
}

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  define: {
    __API_HOST__: JSON.stringify(apiHost),
    __API_PORT__: JSON.stringify(apiPort)
  },
  server: {
    port: 3000
  }
})
