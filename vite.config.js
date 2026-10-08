import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// base: './' 讓 build 出來的 dist/ 用相對路徑，放到 GitHub Pages 子路徑也能跑
export default defineConfig({
  plugins: [vue()],
  base: './',
})
