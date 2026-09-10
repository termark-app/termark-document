import { cp, mkdir, rm } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
const source = fileURLToPath(new URL('../redirect-site/', import.meta.url))
const output = fileURLToPath(new URL('../.vitepress/dist/', import.meta.url))
await rm(output, { recursive: true, force: true })
await mkdir(output, { recursive: true })
for (const file of ['_redirects', '404.html']) await cp(`${source}${file}`, `${output}${file}`)
console.log('Redirect-only site built in .vitepress/dist')
