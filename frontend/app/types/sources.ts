export interface ImportRunInfo {
  started_at: string | null
  finished_at: string | null
  rows: number
  succeeded: boolean | null
}

export interface SourceInfo {
  key: string
  name: string
  logo: string
  role: string
  license: string
  limits: string
  last_import: ImportRunInfo
}

export interface PipelineStep {
  step: number
  name: string
  description: string
}

export interface SourcesOverviewResponse {
  pipeline: {
    steps: PipelineStep[]
  }
  sources: SourceInfo[]
  methodology_notes: string[]
}
