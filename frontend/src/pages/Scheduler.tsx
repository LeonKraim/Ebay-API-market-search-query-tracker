import { useSchedulerStatus, usePauseScheduler, useResumeScheduler, useRunAllNow } from '@/api/hooks'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { Throbber } from '@/components/ui/Throbber'
import { Play, Pause, RotateCcw } from 'lucide-react'

export function SchedulerPage() {
  const { data: status, isLoading } = useSchedulerStatus()
  const pauseMutation = usePauseScheduler()
  const resumeMutation = useResumeScheduler()
  const runAllMutation = useRunAllNow()

  const isPending =
    pauseMutation.isPending || resumeMutation.isPending || runAllMutation.isPending

  return (
    <div className="max-w-xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold text-white">Scheduler</h1>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-6">
        {/* Status */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-400">Status</span>
          {isLoading ? (
            <Throbber />
          ) : (
            <StatusBadge
              status={
                status?.paused ? 'disabled' : status?.running ? 'running' : 'idle'
              }
            />
          )}
        </div>

        {/* Controls */}
        <div className="flex gap-3 flex-wrap">
          <button
            onClick={() => pauseMutation.mutate()}
            disabled={isPending || status?.paused || !status?.active_schedules}
            className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-medium disabled:opacity-40 transition-colors"
          >
            {pauseMutation.isPending ? <Throbber size={14} /> : <Pause className="w-4 h-4" />}
            Pause
          </button>
          <button
            onClick={() => resumeMutation.mutate()}
            disabled={isPending || !status?.paused || !status?.active_schedules}
            className="flex items-center gap-2 px-4 py-2 bg-green-700 hover:bg-green-600 text-white rounded-lg text-sm font-medium disabled:opacity-40 transition-colors"
          >
            {resumeMutation.isPending ? <Throbber size={14} /> : <Play className="w-4 h-4" />}
            Resume
          </button>
          <button
            onClick={() => runAllMutation.mutate()}
            disabled={isPending || !status?.active_schedules}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium disabled:opacity-40 transition-colors"
          >
            {runAllMutation.isPending ? <Throbber size={14} /> : <RotateCcw className="w-4 h-4" />}
            Run all now
          </button>
        </div>

        {(pauseMutation.isSuccess || resumeMutation.isSuccess || runAllMutation.isSuccess) && (
          <p className="text-xs text-green-400">Done.</p>
        )}

        {!isLoading && !status?.running && !status?.paused && status?.active_schedules === 0 && (
          <p className="text-xs text-gray-500">No enabled queries are currently scheduled.</p>
        )}

        {!isLoading && !status?.running && !status?.paused && (status?.active_schedules ?? 0) > 0 && (
          <p className="text-xs text-gray-500">
            {status?.active_schedules} scheduled quer{status?.active_schedules === 1 ? 'y is' : 'ies are'} waiting for the next run.
          </p>
        )}
      </div>
    </div>
  )
}
