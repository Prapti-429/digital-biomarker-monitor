import React, { useState } from 'react';

interface DataPoint { date: string; value: number; baselineMin?: number; baselineMax?: number; }
interface TrendChartProps { data: DataPoint[]; height?: number; label?: string; metricUnit?: string; }

export const TrendChart: React.FC<TrendChartProps> = ({ data, height = 240, label = 'Longitudinal Stability', metricUnit = 'pts' }) => {
  const [activeIdx, setActiveIdx] = useState<number | null>(null);
  if (!data?.length) return <div className="h-60 flex items-center justify-center rounded-xl bg-slate-900/40 border border-slate-800 text-slate-400 text-sm">No longitudinal trend data recorded yet.</div>;

  const width = 700; const padX = 40; const padY = 30;
  const values = data.map(d => d.value);
  const baselines = data.flatMap(d => [d.baselineMin, d.baselineMax]).filter((v): v is number => typeof v === 'number' && Number.isFinite(v));
  const allValues = [...values, ...baselines];
  const minVal = Math.min(...allValues); const maxVal = Math.max(...allValues); const range = maxVal - minVal || 1;
  const getX = (i: number) => data.length === 1 ? width / 2 : padX + (i / (data.length - 1)) * (width - padX * 2);
  const getY = (v: number) => height - padY - ((v - minVal) / range) * (height - padY * 2);
  const points = data.map((d, i) => `${getX(i)},${getY(d.value)}`).join(' ');
  const firstMin = data.find(d => d.baselineMin !== undefined)?.baselineMin;
  const firstMax = data.find(d => d.baselineMax !== undefined)?.baselineMax;

  return <div className="w-full relative">
    <div className="flex items-center justify-between mb-3 text-xs text-slate-400"><span className="font-medium text-slate-300">{label}</span><span>{activeIdx !== null ? `${data[activeIdx].date}: ${data[activeIdx].value} ${metricUnit}` : `Latest: ${data[data.length - 1].value} ${metricUnit}`}</span></div>
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto overflow-visible select-none" role="img" aria-label={`${label} longitudinal graph`}>
      <defs><linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#0EA5E9" stopOpacity="0.25"/><stop offset="100%" stopColor="#0EA5E9" stopOpacity="0"/></linearGradient></defs>
      {[0.25,0.5,0.75,1].map((pct,i) => { const y = height-padY-pct*(height-padY*2); return <line key={i} x1={padX} y1={y} x2={width-padX} y2={y} stroke="#1E293B" strokeDasharray="4 4"/>; })}
      {firstMin !== undefined && firstMax !== undefined && <rect x={padX} y={Math.min(getY(firstMin), getY(firstMax))} width={width-padX*2} height={Math.abs(getY(firstMin)-getY(firstMax))} fill="#14B8A6" fillOpacity="0.08"/>}
      <polygon points={`${getX(0)},${height-padY} ${points} ${getX(data.length-1)},${height-padY}`} fill="url(#chartGradient)"/>
      <polyline fill="none" stroke="#0EA5E9" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" points={points}/>
      {data.map((d,i) => { const cx=getX(i); const cy=getY(d.value); const hovered=activeIdx===i; return <g key={`${d.date}-${i}`} className="cursor-pointer" onMouseEnter={() => setActiveIdx(i)}><circle cx={cx} cy={cy} r={hovered?6:4} fill={hovered?'#38BDF8':'#0B0F17'} stroke="#0EA5E9" strokeWidth="2"/><text x={cx} y={height-10} textAnchor="middle" className="text-[10px] fill-slate-500 font-mono">{d.date}</text></g>; })}
    </svg>
    {firstMin !== undefined && firstMax !== undefined && <div className="mt-2 text-[10px] text-slate-500">Shaded area = your recent personal range ({firstMin}–{firstMax}).</div>}
  </div>;
};