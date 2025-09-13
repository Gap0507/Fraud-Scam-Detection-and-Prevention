'use client'

import { useState, useRef, useEffect } from 'react'
import { AudioAnalysisResponse } from '@/types/analysis'
import { 
  analyzeAudioGemini, 
  analyzeVideoGemini
} from '@/services/api'
import { 
  Upload, 
  FileAudio, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Volume2,
  Brain,
  Play,
  Square,
  Plus,
  AlertTriangle as ExclamationTriangleIcon,
  Info
} from 'lucide-react'
import MainLayout from '@/components/MainLayout'

interface AudioFile {
  id: string
  name: string
  size: number
  type: string
  timestamp: string
  analysis?: AudioAnalysisResponse
  isAnalyzed: boolean
  riskScore: 'HIGH' | 'MEDIUM' | 'LOW'
}

export default function VoiceChannelsPage() {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AudioAnalysisResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  useEffect(() => {
    checkBackendStatus()
  }, [])

  const checkBackendStatus = async () => {
    setBackendStatus('checking')
    try {
      const response = await fetch('http://localhost:8000/health')
      setBackendStatus(response.ok ? 'online' : 'offline')
    } catch {
      setBackendStatus('offline')
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setAnalysisResult(null)
      setError(null)
    }
  }

  const handleAnalyzeAudio = async () => {
    if (!selectedFile) return

    setIsAnalyzing(true)
    setError(null)

    try {
      const result = await analyzeAudioGemini(selectedFile)
      setAnalysisResult(result)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        const audioFile = new File([audioBlob], 'recording.wav', { type: 'audio/wav' })
        setSelectedFile(audioFile)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (err) {
      setError('Failed to access microphone')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }


  const formatFileSize = (size: number) => {
    return `${size.toFixed(1)} MB`
  }

  return (
    <MainLayout>
      {/* Header */}
      <header className="flex items-center justify-between p-6 border-b border-[#21262d]">
        <div>
          <h2 className="text-3xl font-bold">Voice Channels</h2>
          <div className="flex items-center gap-2 mt-1">
            <div className={`w-2 h-2 rounded-full ${
              backendStatus === 'online' ? 'bg-green-400' :
              backendStatus === 'offline' ? 'bg-red-400' :
              'bg-yellow-400 animate-pulse'
            }`} />
            <span className="text-sm text-gray-400">
              {backendStatus === 'online' ? 'AI Backend Online' :
               backendStatus === 'offline' ? 'AI Backend Offline' :
               'Checking Backend...'}
            </span>
          </div>
        </div>
      </header>

      {/* Content Area */}
      <div className="flex-1 flex">
        {/* Center Upload Interface */}
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="w-full max-w-2xl">
            <div className="bg-[#0D1117] rounded-lg border border-[#21262d] p-8 text-center">
              {/* Large Microphone Icon */}
              <div className="flex justify-center mb-6">
                <div className="w-24 h-24 bg-[var(--accent-teal)]/20 rounded-full flex items-center justify-center border-2 border-[var(--accent-teal)]/30">
                  <Volume2 className="w-12 h-12 text-[var(--accent-teal)]" />
                </div>
              </div>

              {/* Upload Title */}
              <h3 className="text-2xl font-bold text-white mb-2">Upload Audio for Analysis</h3>
              <p className="text-gray-400 mb-8">Upload an audio file or record directly to analyze for deepfake detection</p>

              {/* Upload Options */}
              <div className="space-y-4">
                {/* File Upload */}
                <div className="flex flex-col items-center gap-4">
                  <input
                    type="file"
                    accept="audio/*"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="audio-upload"
                  />
                  <label
                    htmlFor="audio-upload"
                    className="w-full max-w-md flex items-center justify-center gap-3 px-6 py-4 bg-[#161b22] border-2 border-dashed border-[#21262d] rounded-lg text-white hover:border-[var(--accent-teal)]/50 hover:bg-[#161b22]/80 transition-colors cursor-pointer"
                  >
                    <Upload className="w-5 h-5 text-[var(--accent-teal)]" />
                    <span className="font-medium">Choose Audio File</span>
                  </label>
                </div>

                {/* Divider */}
                <div className="flex items-center gap-4">
                  <div className="flex-1 h-px bg-[#21262d]"></div>
                  <span className="text-gray-500 text-sm">or</span>
                  <div className="flex-1 h-px bg-[#21262d]"></div>
                </div>

                {/* Record Button */}
                <div className="flex flex-col items-center gap-4">
                  <button
                    onClick={isRecording ? stopRecording : startRecording}
                    className={`w-full max-w-md flex items-center justify-center gap-3 px-6 py-4 rounded-lg font-semibold transition-colors ${
                      isRecording 
                        ? 'bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30' 
                        : 'bg-[var(--accent-teal)]/20 text-[var(--accent-teal)] border border-[var(--accent-teal)]/30 hover:bg-[var(--accent-teal)]/30'
                    }`}
                  >
                    {isRecording ? (
                      <>
                        <Square className="w-5 h-5" />
                        Stop Recording
                      </>
                    ) : (
                      <>
                        <Volume2 className="w-5 h-5" />
                        Record Audio
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Selected File Display */}
              {selectedFile && (
                <div className="mt-6 p-4 bg-[#161b22] rounded-lg border border-[#21262d]">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <FileAudio className="w-5 h-5 text-[var(--accent-teal)]" />
                      <div className="text-left">
                        <p className="text-white font-medium">{selectedFile.name}</p>
                        <p className="text-gray-400 text-sm">{formatFileSize(selectedFile.size / 1024 / 1024)}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setSelectedFile(null)}
                      className="text-gray-400 hover:text-white transition-colors"
                    >
                      <span className="material-symbols-outlined">close</span>
                    </button>
                  </div>
                  <button
                    onClick={handleAnalyzeAudio}
                    disabled={isAnalyzing}
                    className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-[var(--accent-teal)]/20 text-[var(--accent-teal)] border border-[var(--accent-teal)]/30 rounded-lg hover:bg-[var(--accent-teal)]/30 transition-colors disabled:opacity-50"
                  >
                    <Brain className="w-4 h-4" />
                    {isAnalyzing ? 'Analyzing...' : 'Analyze with AI'}
                  </button>
                </div>
              )}

              {/* Error Display */}
              {error && (
                <div className="mt-4 p-3 bg-red-500/20 border border-red-500/30 rounded-lg">
                  <div className="flex items-center justify-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-red-400" />
                    <span className="text-red-400 text-sm">{error}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Analysis Results Panel */}
        {analysisResult && (
          <div className="w-96 bg-[#010409] border-l border-[#21262d] p-6 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold">Analysis Results</h3>
              <button
                onClick={() => {
                  setAnalysisResult(null)
                }}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            <div className="flex-1 bg-[#0D1117] rounded-lg p-4 border border-[#21262d]">
              {(() => {
                const result = analysisResult
                if (!result) return null

                return (
                  <>
                    <div className="flex items-center gap-3 mb-4">
                      <div className={`w-16 h-16 rounded-full flex items-center justify-center ${
                        result.is_deepfake ? 'bg-red-500' : 'bg-green-500'
                      }`}>
                        {result.is_deepfake ? (
                          <AlertTriangle className="w-8 h-8 text-white" />
                        ) : (
                          <CheckCircle className="w-8 h-8 text-white" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="text-white font-semibold">
                          {result.is_deepfake ? 'Deepfake Detected' : 'Genuine Content'}
                        </p>
                        <p className="text-gray-400 text-sm">
                          {result.is_deepfake ? 'HIGH RISK' : 'LOW RISK'}
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-white">
                          {(result.confidence * 100).toFixed(1)}%
                        </div>
                        <p className="text-sm text-gray-400">Confidence</p>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-white">
                          {result.processing_time?.toFixed(2)}s
                        </div>
                        <p className="text-sm text-gray-400">Processing Time</p>
                      </div>
                    </div>

                    <div className="mb-4">
                      <h4 className="text-white font-semibold mb-2">Analysis Details</h4>
                      <p className="text-gray-300 text-sm leading-relaxed">
                        {result.explanation}
                      </p>
                    </div>

                    {result.triggers && result.triggers.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-white font-semibold mb-2">Detected Indicators</h4>
                        <div className="flex flex-wrap gap-2">
                          {result.triggers.map((trigger: string, index: number) => (
                            <span
                              key={index}
                              className="bg-red-500/20 text-red-400 text-xs font-medium px-2 py-1 rounded-full"
                            >
                              {trigger}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="text-xs text-gray-500 mt-4">
                      <p>Analysis ID: {result.analysis_id}</p>
                      <p>Timestamp: {new Date(result.timestamp).toLocaleString()}</p>
                    </div>
                  </>
                )
              })()}
            </div>
          </div>
        )}
      </div>

    </MainLayout>
  )
}