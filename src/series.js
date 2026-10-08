// 三條序列的固定顏色與標籤：顏色跟著「實體」走，不跟著順序走。
// 實際色票定義在 style.css 的 CSS custom properties（含深色模式）。
export const SERIES = [
  { key: 'source_a', label: '來源 A：110 Hz 基頻 + 220 Hz 泛音', color: 'var(--series-1)' },
  { key: 'source_b', label: '來源 B：350 Hz 基頻 + 700 Hz 泛音', color: 'var(--series-2)' },
  { key: 'mixture',  label: '混合訊號：A + B + 白雜訊 (σ = 0.12)', color: 'var(--series-3)' },
]

export const SOURCE_NAME = { source_a: '來源 A', source_b: '來源 B' }
export const SOURCE_COLOR = { source_a: 'var(--series-1)', source_b: 'var(--series-2)' }
export const MIX_COLOR = 'var(--series-3)'
