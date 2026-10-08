<script setup>
// 圖 2：混合訊號的振幅頻譜（面積 + 折線），並在四個峰值直接標註來源、頻率與振幅。
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'
import { SOURCE_NAME, SOURCE_COLOR, MIX_COLOR } from '../series.js'

const props = defineProps({
  rows: { type: Array, required: true },   // spectrum.csv：{ freq_hz, source_a, source_b, mixture }
  peaks: { type: Array, required: true },  // 已含 measured 的峰值：{ source, freq_hz, amplitude, measured }
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

  const H = 320
  const TOP = 44
  const BOTTOM = 46
  const plotW = W - ML - MR

  const svg = d3.select(el).append('svg')
    .attr('viewBox', [0, 0, W, H])
    .attr('role', 'img')
    .attr('aria-label', `混合訊號 0 到 ${props.fmax} Hz 的振幅頻譜，標出來源 A 與來源 B 的峰值`)

  const x = d3.scaleLinear().domain([0, props.fmax]).range([ML, W - MR])
  const yMax = Math.max(1, d3.max(rows, d => d.mixture))
  const y = d3.scaleLinear().domain([0, yMax * 1.12]).range([H - BOTTOM, TOP])

  // 格線、座標軸、軸標籤
  svg.append('g').attr('class', 'grid').attr('transform', `translate(${ML},0)`)
    .call(d3.axisLeft(y).ticks(4).tickSize(-plotW).tickFormat(''))
  svg.append('g').attr('class', 'axis').attr('transform', `translate(${ML},0)`)
    .call(d3.axisLeft(y).ticks(4).tickSize(4).tickFormat(d3.format('.1f')))
    .call(g => g.select('.domain').remove())
  svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${H - BOTTOM})`)
    .call(d3.axisBottom(x).ticks(10).tickSize(4))
    .call(g => g.select('.domain').remove())
  svg.append('text').attr('class', 'axis-label')
    .attr('x', W - MR).attr('y', H - 8).attr('text-anchor', 'end').text('頻率 (Hz)')
  svg.append('text').attr('class', 'axis-label').attr('x', ML - 44).attr('y', TOP - 10).text('振幅')

  // 頻譜：淡色面積 + 折線
  svg.append('path').datum(rows)
    .style('fill', MIX_COLOR).attr('fill-opacity', 0.12)
    .attr('d', d3.area().x(d => x(d.freq_hz)).y0(y(0)).y1(d => y(d.mixture)))
  svg.append('path').datum(rows)
    .attr('fill', 'none').style('stroke', MIX_COLOR)
    .attr('stroke-width', 1.75).attr('stroke-linejoin', 'round')
    .attr('d', d3.line().x(d => x(d.freq_hz)).y(d => y(d.mixture)))

  // 峰值標註：圓點（外圈留 2px 底色）+ 兩行文字 + 滑鼠停留的 tooltip
  const marks = props.peaks.filter(p => p.freq_hz <= props.fmax)
  const g = svg.append('g').selectAll('g').data(marks).join('g')
    .attr('transform', d => `translate(${x(d.freq_hz)},${y(d.measured)})`)
  g.append('circle').attr('r', 5.5)
    .style('fill', d => SOURCE_COLOR[d.source])
    .style('stroke', 'var(--surface-1)').attr('stroke-width', 2)
  g.append('text').attr('class', 'peak-label').attr('text-anchor', 'middle').attr('y', -22)
    .text(d => `${SOURCE_NAME[d.source]} ${d.freq_hz} Hz`)
  g.append('text').attr('class', 'peak-sub').attr('text-anchor', 'middle').attr('y', -10)
    .text(d => `振幅 ${d.measured.toFixed(2)}`)
  g.append('title')
    .text(d => `${SOURCE_NAME[d.source]}：${d.freq_hz} Hz\n設定振幅 ${d.amplitude.toFixed(2)}，頻譜量測 ${d.measured.toFixed(3)}`)

  // 圖例（右上角，從右往左排）
  const legend = svg.append('g').attr('class', 'legend').attr('transform', `translate(${W - MR},${TOP - 30})`)
  const items = [
    { label: '混合訊號頻譜', color: MIX_COLOR, kind: 'line' },
    { label: '來源 A 的成分', color: SOURCE_COLOR.source_a, kind: 'dot' },
    { label: '來源 B 的成分', color: SOURCE_COLOR.source_b, kind: 'dot' },
  ]
  let cursor = 0
  items.slice().reverse().forEach(it => {
    const li = legend.append('g')
    li.append('text').attr('x', -cursor).attr('y', 4).attr('text-anchor', 'end').text(it.label)
    const tw = it.label.length * 11.5 + 4
    if (it.kind === 'dot') {
      li.append('circle').attr('cx', -cursor - tw - 6).attr('cy', 0).attr('r', 4.5).style('fill', it.color)
    } else {
      li.append('line')
        .attr('x1', -cursor - tw - 14).attr('x2', -cursor - tw).attr('y1', 0).attr('y2', 0)
        .style('stroke', it.color).attr('stroke-width', 2.5)
    }
    cursor += tw + 30
  })
}

onMounted(draw)
watch(() => [props.rows, props.peaks, props.fmax], draw, { flush: 'post' })
</script>

<template>
  <div ref="host" class="chart"></div>
</template>
