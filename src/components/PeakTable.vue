<script setup>
// 資料表：讓數值不靠顏色也能閱讀（無障礙用）。這裡純用 Vue 模板渲染，不需要 D3。
import { SOURCE_NAME, SOURCE_COLOR } from '../series.js'

defineProps({
  peaks: { type: Array, required: true },  // { source, freq_hz, amplitude, measured }
})
</script>

<template>
  <details>
    <summary>資料表：各頻率成分的設定振幅與頻譜量測值</summary>
    <table>
      <thead>
        <tr>
          <th>音源</th>
          <th class="num">頻率</th>
          <th class="num">設定振幅</th>
          <th class="num">頻譜量測</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in peaks" :key="`${p.source}-${p.freq_hz}`">
          <td><span class="swatch" :style="{ background: SOURCE_COLOR[p.source] }"></span>{{ SOURCE_NAME[p.source] }}</td>
          <td class="num">{{ p.freq_hz }} Hz</td>
          <td class="num">{{ p.amplitude.toFixed(2) }}</td>
          <td class="num">{{ p.measured.toFixed(3) }}</td>
        </tr>
      </tbody>
    </table>
  </details>
</template>
