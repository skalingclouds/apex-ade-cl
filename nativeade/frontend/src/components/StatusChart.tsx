import { DocumentStats } from '../services/api'

interface StatusChartProps {
  data: DocumentStats | undefined
}

export default function StatusChart({ data }: StatusChartProps) {
  if (!data || data.total === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-400">No data available</p>
      </div>
    )
  }

  const radius = 80
  const strokeWidth = 20
  const circumference = 2 * Math.PI * radius
  const completedOffset = circumference - (data.completed / data.total) * circumference

  return (
    <div className="flex items-center justify-center">
      <div className="relative">
        <svg width={200} height={200} className="transform -rotate-90">
          {/* Background circle */}
          <circle
            cx={100}
            cy={100}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="none"
            className="text-dark-700"
          />
          {/* Completed arc */}
          <circle
            cx={100}
            cy={100}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={completedOffset}
            className="text-accent-green transition-all duration-1000"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold">{data.completed}</span>
          <span className="text-sm text-gray-400">Completed</span>
        </div>
      </div>
    </div>
  )
}