<script setup>
// 圖 1：三個小面板 (small multiples)，各畫一條時域波形，共用 x / y 刻度。
// Vue 負責元件生命週期與資料流，D3 負責比例尺、座標軸與 SVG 繪圖。
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'
import { SERIES } from '../series.js'

const props = defineProps({
  rows: { type: Array, required: true },    // waveform.csv：{ t, source_a, source_b, noise, mixture }
  windowMs: { type: Number, default: 50 },  // 只畫前幾毫秒，波形才看得清楚
})

const host = ref(null)
const W = 880
const ML = 60
const MR = 28

function draw() {
  const el = host.value
  if (!el) return
  d3.select(el).selectAll('*').remove()

  const rows = props.rows.filter(d => d.t * 1000 <= props.windowMs)
  if (!rows.length) return

  const PH = 104   // 每個面板的繪圖高度
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
    .attr('aria-label', `來源 A、來源 B 與混合訊號前 ${props.windowMs} 毫秒的時域波形，三個面板上下排列`)

  const x = d3.scaleLinear().domain([0, props.windowMs]).range([ML, W - MR])
  const absMax = d3.max(rows, d => Math.max(Math.abs(d.source_a), Math.abs(d.source_b), Math.abs(d.mixture)))
  const yMax = Math.ceil(absMax * 2) / 2   // 取到 0.5 的倍數，三個面板共用

  SERIES.forEach((s, i) => {
    const top = TOP + i * (TITLE + PH + GAP) + TITLE
    const y = d3.scaleLinear().domain([-yMax, yMax]).range([top + PH, top])

    // 面板標題 + 色塊
    svg.append('rect')
      .attr('x', ML).attr('y', top - 17).attr('width', 10).attr('height', 10).attr('rx', 2)
      .style('fill', s.color)
    svg.append('text').attr('class', 'panel-title').attr('x', ML + 16).attr('y', top - 8).text(s.label)

    // 格線與 y 軸（只放 -max / 0 / +max 三個刻度，畫面才乾淨）
    svg.append('g').attr('class', 'grid').attr('transform', `translate(${ML},0)`)
      .call(d3.axisLeft(y).tickValues([-yMax, 0, yMax]).tickSize(-plotW).tickFormat(''))
    svg.append('g').attr('class', 'axis').attr('transform', `translate(${ML},0)`)
      .call(d3.axisLeft(y).tickValues([-yMax, 0, yMax]).tickSize(4).tickFormat(d3.format('+.1f')))
      .call(g => g.select('.domain').remove())

    // 波形
    svg.append('path').datum(rows)
      .attr('fill', 'none')
      .style('stroke', s.color)
      .attr('stroke-width', 2)
      .attr('stroke-linejoin', 'round')
      .attr('stroke-linecap', 'round')
      .attr('d', d3.line().x(d => x(d.t * 1000)).y(d => y(d[s.key])))
  })

  // 共用的 x 軸只畫在最下面
  svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${lastBottom + 6})`)
    .call(d3.axisBottom(x).ticks(10).tickSize(4))
    .call(g => g.select('.domain').remove())
  svg.append('text').attr('class', 'axis-label')
    .attr('x', W - MR).attr('y', lastBottom + 40).attr('text-anchor', 'end').text('時間 (ms)')
  svg.append('text').attr('class', 'axis-label').attr('x', ML - 44).attr('y', TOP + 10).text('振幅')
}

onMounted(draw)
watch(() => [props.rows, props.windowMs], draw, { flush: 'post' })
</script>

<template>
  <div ref="host" class="chart"></div>
</template>
