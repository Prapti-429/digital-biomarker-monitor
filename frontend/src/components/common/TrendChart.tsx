import React, { useState } from 'react';

interface DataPoint {
  date: string;
  value: number;
  baselineMin?: number;
  baselineMax?: number;
}

interface TrendChartProps {
  data: DataPoint[];
  height?: number;
  label?: string;
  metricUnit?: string;
}

export const TrendChart: React.FC<TrendChartProps> = ({
  data,
  height = 240,
  label = 'Longitudinal Stability',
  metricUnit = 'pts'
}) => {
  const [activeIdx, setActiveIdx] = useState<number | null>(null);

  if (!data || data.length === 0) {
    return (
      <div className="h-60 flex items-center justify-center rounded-xl bg-slate-900/40 border border-slate-800 text-slate-400 text-sm">
        No longitudinal trend data recorded yet.
      </div>
    );
  }

  const width = 700;
  const padX = 40;
  const padY = 30;
  const values = data.map((d) => d.value);
  const minVal = Math.min(...values, 50);
  const maxVal = Math.max(...values, 100);
  const range = maxVal - minVal || 1;

  const getX = (index: number) => padX + (index / (data.length - 1)) * (width - padX * 2);
  const getY = (val: number) => height - padY - ((val - minVal) / range) * (height - padY * 2);

  const points = data.map((d, i) => `${getX(i)},${getY(d.value)}`).join(' ');

  // Gradient area
  const areaPoints = `${getX(0)},${height - padY} ${points} ${getX(data.length - 1)},${height - padY}`;

  return (
    <div className="w-full relative">
      <div className="flex items-center justify-between mb-3 text-xs text-slate-400">
        <span className="font-medium text-slate-300">{label}</span>
        <span>
          {activeIdx !== null
            ? `${data[activeIdx].date}: ${data[activeIdx].value} ${metricUnit}`
            : `Latest: ${data[data.length - 1].value} ${metricUnit}`}
        </span>
      </div>

      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-auto overflow-visible select-none"
      >
        <defs>
          <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#0EA5E9" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#0EA5E9" stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {/* Horizontal grid lines */}
        {[0.25, 0.5, 0.75, 1].map((pct, i) => {
          const y = height - padY - pct * (height - padY * 2);
          return (
            <line
              key={i}
              x1={padX}
              y1={y}
              x2={width - padX}
              y2={y}
              stroke="#1E293B"
              strokeDasharray="4 4"
            />
          );
        })}

        {/* Baseline Range Shading (e.g. 75 - 90) */}
        <rect
          x={padX}
          y={getY(90)}
          width={width - padX * 2}
          height={Math.abs(getY(75) - getY(90))}
          fill="#14B8A6"
          fillOpacity="0.05"
        />

        {/* Area fill */}
        <polygon points={areaPoints} fill="url(#chartGradient)" />

        {/* Line curve */}
        <polyline
          fill="none"
          stroke="#0EA5E9"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={points}
        />

        {/* Interactive points */}
        {data.map((d, i) => {
          const cx = getX(i);
          const cy = getY(d.value);
          const isHovered = activeIdx === i;
          return (
            <g key={i} className="cursor-pointer" onMouseEnter={() => setActiveIdx(i)}>
              <circle
                cx={cx}
                cy={cy}
                r={isHovered ? 6 : 4}
                className="transition-all duration-150"
                fill={isHovered ? '#38BDF8' : '#0B0F17'}
                stroke="#0EA5E9"
                strokeWidth="2"
              />
              <text
                x={cx}
                y={height - 10}
                textAnchor="middle"
                className="text-[10px] fill-slate-500 font-mono"
              >
                {d.date}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};