<script setup>
// 圖 2：三個小面板 (small multiples)，各畫一條振幅頻譜（面積 + 折線），
// 排列順序、顏色與畫法都和圖 1 一致：來源 A、來源 B、混合訊號各一個面板，共用 x / y 刻度。
// 峰值只用文字標註（不另外畫圓點），讓三條序列維持同一種視覺編碼。
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'
import { SERIES, SOURCE_NAME } from '../series.js'

const props = defineProps({
  rows: { type: Array, required: true },   // spectrum.csv：{ freq_hz, source_a, source_b, mixture }
  peaks: { type: Array, required: true },  // 各音源的頻率成分：{ source, freq_hz, amplitude }
  fmax: { type: Number, default: 1000 },   // 只畫到這個頻率
})

const host = ref(null)
const W = 880
const ML = 60
const MR = 28

function draw() {
  const el = host.value
  if (!el) return
  d3.select(el).selectAll('*').remove()

  const rows = props.rows.filter(d => d.freq_hz <= props.fmax)
  if (!rows.length) return

  const PH = 118   // 每個面板的繪圖高度
  const TITLE = 24 // 面板標題保留高度
  const GAP = 16
  const TOP = 6
  const n = SERIES.length
  const lastBottom = TOP + (n - 1) * (TITLE + PH + GAP) + TITLE + PH
  const H = lastBottom + 46
  const plotW = W - ML - MR

  const svg = d3.select(el).append('svg')
    .attr('viewBox', [0, 0, W, H])
    .attr('role', 'img')
    .attr('aria-label', `來源 A、來源 B 與混合訊號 0 到 ${props.fmax} Hz 的振幅頻譜，三個面板上下排列，峰值標出頻率與振幅`)

  const x = d3.scaleLinear().domain([0, props.fmax]).range([ML, W - MR])
  // 三個面板共用同一個 y 刻度；上方多留 35% 放峰值文字
  const absMax = d3.max(rows, d => Math.max(d.source_a, d.source_b, d.mixture))
  const yMax = Math.max(1, Math.ceil(absMax * 10) / 10)
  const yTicks = d3.range(0, yMax + 1e-9, 0.5)

  // 每個面板要標註的峰值：來源面板標自己的成分，混合訊號面板標全部四個
  const peaksFor = key => props.peaks
    .filter(p => p.freq_hz <= props.fmax && (key === 'mixture' || p.source === key))
    .map(p => {
      const bin = d3.least(rows, d => Math.abs(d.freq_hz - p.freq_hz))
      return { ...p, measured: bin ? bin[key] : NaN }
    })

  SERIES.forEach((s, i) => {
    const top = TOP + i * (TITLE + PH + GAP) + TITLE
    const y = d3.scaleLinear().domain([0, yMax * 1.35]).range([top + PH, top])

    // 面板標題 + 色塊（與圖 1 相同）
    svg.append('rect')
      .attr('x', ML).attr('y', top - 17).attr('width', 10).attr('height', 10).attr('rx', 2)
      .style('fill', s.color)
    svg.append('text').attr('class', 'panel-title').attr('x', ML + 16).attr('y', top - 8).text(s.label)

    // 格線與 y 軸
    svg.append('g').attr('class', 'grid').attr('transform', `translate(${ML},0)`)
      .call(d3.axisLeft(y).tickValues(yTicks).tickSize(-plotW).tickFormat(''))
    svg.append('g').attr('class', 'axis').attr('transform', `translate(${ML},0)`)
      .call(d3.axisLeft(y).tickValues(yTicks).tickSize(4).tickFormat(d3.format('.1f')))
      .call(g => g.select('.domain').remove())

    // 頻譜：淡色面積 + 折線，三個面板一樣的畫法
    svg.append('path').datum(rows)
      .style('fill', s.color).attr('fill-opacity', 0.12)
      .attr('d', d3.area().x(d => x(d.freq_hz)).y0(y(0)).y1(d => y(d[s.key])))
    svg.append('path').datum(rows)
      .attr('fill', 'none').style('stroke', s.color)
      .attr('stroke-width', 1.75).attr('stroke-linejoin', 'round')
      .attr('d', d3.line().x(d => x(d.freq_hz)).y(d => y(d[s.key])))

    // 峰值標註：純文字兩行（頻率 / 量測振幅），混合訊號面板多寫是哪個來源
    const g = svg.append('g').selectAll('g').data(peaksFor(s.key)).join('g')
      .attr('transform', d => `translate(${x(d.freq_hz)},${y(d.measured)})`)
    g.append('text').attr('class', 'peak-label').attr('text-anchor', 'middle').attr('y', -18)
      .text(d => (s.key === 'mixture' ? `${SOURCE_NAME[d.source]} ` : '') + `${d.freq_hz} Hz`)
    g.append('text').attr('class', 'peak-sub').attr('text-anchor', 'middle').attr('y', -6)
      .text(d => d.measured.toFixed(2))
    g.append('title')
      .text(d => `${SOURCE_NAME[d.source]}：${d.freq_hz} Hz\n設定振幅 ${d.amplitude.toFixed(2)}，${s.label.split('：')[0]}頻譜量測 ${d.measured.toFixed(3)}`)
  })

  // 共用的 x 軸只畫在最下面
  svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${lastBottom + 6})`)
    .call(d3.axisBottom(x).ticks(10).tickSize(4))
    .call(g => g.select('.domain').remove())
  svg.append('text').attr('class', 'axis-label')
    .attr('x', W - MR).attr('y', lastBottom + 40).attr('text-anchor', 'end').text('頻率 (Hz)')
  svg.append('text').attr('class', 'axis-label').attr('x', ML - 44).attr('y', TOP + 10).text('振幅')
}

onMounted(draw)
watch(() => [props.rows, props.peaks, props.fmax], draw, { flush: 'post' })
</script>

<template>
  <div ref="host" class="chart"></div>
</template>
