<script setup>
import { ref, computed, onMounted } from 'vue'
import * as d3 from 'd3'
import WaveformChart from './components/WaveformChart.vue'
import SpectrumChart from './components/SpectrumChart.vue'
import PeakTable from './components/PeakTable.vue'

// public/data/*.csv 由 generate_data.py 產生；BASE_URL 讓 dev 與 build 後的相對路徑都正確
const base = import.meta.env.BASE_URL
const waveform = ref([])
const spectrum = ref([])
const peaks = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const [w, s, p] = await Promise.all([
      d3.csv(`${base}data/waveform.csv`, d3.autoType),
      d3.csv(`${base}data/spectrum.csv`, d3.autoType),
      d3.csv(`${base}data/peaks.csv`, d3.autoType),
    ])
    waveform.value = w
    spectrum.value = s
    peaks.value = p
  } catch (e) {
    error.value = `資料載入失敗：${e.message}\n請先執行 python3 generate_data.py 產生 public/data/*.csv。`
  } finally {
    loading.value = false
  }
})

// 每個頻率成分在混合訊號頻譜上實際量到的峰值（找最接近的 bin）
const measuredPeaks = computed(() =>
  peaks.value.map(p => {
    const bin = d3.least(spectrum.value, d => Math.abs(d.freq_hz - p.freq_hz))
    return { ...p, measured: bin ? bin.mixture : NaN }
  }),
)
</script>

<template>
  <main>
    <header>
      <h1>音訊混合訊號的時域與頻域視覺化</h1>
      <p>兩個音源 A、B 加上白雜訊疊成一條混合訊號。時域裡三者纏在一起，但轉到頻域後，每個音源的頻率成分就各自分開了：這正是音訊分離 (source separation) 的起點。</p>
      <p class="meta">1151VIS HW1 · 靜態視覺化 · Vue 3 + D3.js v7 · 資料由 <code>generate_data.py</code> 以純 Python 合成（取樣率 4096 Hz、0.5 秒）</p>
    </header>

    <p v-if="loading" class="status">資料載入中…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <template v-else>
      <figure>
        <h2>圖 1　時域波形（前 50 ms）</h2>
        <p class="desc">三個面板共用同一組時間軸與振幅刻度。來源 A 是 110 Hz 的低音（含 220 Hz 泛音），來源 B 是 350 Hz 的高音（含 700 Hz 泛音）；混合訊號 = A + B + 雜訊。</p>
        <WaveformChart :rows="waveform" :window-ms="50" />
      </figure>

      <figure>
        <h2>圖 2　混合訊號的振幅頻譜（0–1000 Hz）</h2>
        <p class="desc">對 0.5 秒的混合訊號做 Hann 視窗 + FFT。四個峰值對應兩個音源的基頻與泛音，峰高幾乎等於原始振幅，雜訊則攤成底部的細小起伏。</p>
        <SpectrumChart :rows="spectrum" :peaks="measuredPeaks" :fmax="1000" />
        <PeakTable :peaks="measuredPeaks" />
      </figure>
    </template>

    <footer>
      執行方式：<code>npm install</code> 之後 <code>npm run dev</code>，開啟終端機顯示的網址（預設 http://localhost:5173/）。
      資料由 <code>python3 generate_data.py</code> 產生在 <code>public/data/</code>。
    </footer>
  </main>
</template>
