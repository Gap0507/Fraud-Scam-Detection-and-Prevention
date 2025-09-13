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
  const [audioFiles, setAudioFiles] = useState<AudioFile[]>([])
  const [selectedAudioFile, setSelectedAudioFile] = useState<AudioFile | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  // Demo audio files for initial load
  const demoAudioFiles: AudioFile[] = [
    {
      id: '1',
      name: 'margot-original.wav',
      size: 13.37,
      type: 'audio/wav',
      timestamp: '2 hours ago',
      isAnalyzed: true,
      riskScore: 'LOW',
      analysis: {
        analysis_id: 'demo_1',
        channel: 'voice',
        risk_score: 0.15,
        risk_level: 'LOW',
        highlighted_tokens: [],
        is_fraud: false,
        triggers: [],
        explanation: 'The audio appears to be a recording of a woman reading a statement, purportedly written by someone else (Brad), at an event or awards ceremony. The speech contains several characteristics indicative of genuine human speech, including hesitations, natural speech rhythm and intonation.',
        confidence: 0.85,
        processing_time: 7.85,
        timestamp: new Date().toISOString(),
        audio_file: 'margot-original.wav',
        deepfake_score: 0.15,
        is_deepfake: false,
        audio_metadata: {
          file_size: 14000000,
          file_type: 'wav',
          analysis_method: 'gemini_2_5_pro'
        }
      }
    },
    {
      id: '2',
      name: 'suspicious-call.mp3',
      size: 8.2,
      type: 'audio/mp3',
      timestamp: '4 hours ago',
      isAnalyzed: true,
      riskScore: 'HIGH',
      analysis: {
        analysis_id: 'demo_2',
        channel: 'voice',
        risk_score: 0.92,
        risk_level: 'HIGH',
        highlighted_tokens: [],
        is_fraud: true,
        triggers: ['synthetic voice patterns', 'artificial intonation'],
        explanation: 'This audio shows clear signs of synthetic generation with unnatural voice patterns and artificial intonation that are characteristic of deepfake technology.',
        confidence: 0.92,
        processing_time: 5.23,
        timestamp: new Date().toISOString(),
        audio_file: 'suspicious-call.mp3',
        deepfake_score: 0.92,
        is_deepfake: true,
        audio_metadata: {
          file_size: 8600000,
          file_type: 'mp3',
          analysis_method: 'gemini_2_5_pro'
        }
      }
    },
    {
      id: '3',
      name: 'meeting-recording.flac',
      size: 25.1,
      type: 'audio/flac',
      timestamp: '1 day ago',
      isAnalyzed: false,
      riskScore: 'LOW'
    }
  ]

  useEffect(() => {
    setAudioFiles(demoAudioFiles)
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
      
      // Add to audio files list
      const newAudioFile: AudioFile = {
        id: Date.now().toString(),
        name: selectedFile.name,
        size: selectedFile.size / 1024 / 1024,
        type: selectedFile.type,
        timestamp: 'Just now',
        isAnalyzed: true,
        riskScore: result.risk_level as 'HIGH' | 'MEDIUM' | 'LOW',
        analysis: result
      }
      
      setAudioFiles(prev => [newAudioFile, ...prev])
      setSelectedAudioFile(newAudioFile)
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

  const analyzeAudioFile = async (audioFile: AudioFile) => {
    if (audioFile.isAnalyzed || isAnalyzing) return

    setIsAnalyzing(true)
    try {
      // Create a File object from the audio file data
      const file = new File([], audioFile.name, { type: audioFile.type })
      const result = await analyzeAudioGemini(file)

      setAudioFiles(prev => prev.map(f => 
        f.id === audioFile.id 
          ? { 
              ...f, 
              analysis: result,
              isAnalyzed: true,
              riskScore: result.risk_level as 'HIGH' | 'MEDIUM' | 'LOW'
            }
          : f
      ))

    } catch (error) {
      console.error('Analysis failed:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getRiskScoreColor = (risk: string) => {
    switch (risk) {
      case 'HIGH':
        return 'bg-red-500/20 text-red-400'
      case 'MEDIUM':
        return 'bg-yellow-500/20 text-yellow-400'
      case 'LOW':
        return 'bg-green-500/20 text-green-400'
      default:
        return 'bg-gray-500/20 text-gray-400'
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-400'
    if (confidence >= 0.6) return 'text-yellow-400'
    return 'text-red-400'
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
        {/* Audio Files List */}
        <div className="flex-1 p-6">
          <div className="bg-[#0D1117] rounded-lg border border-[#21262d] overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-[#161b22] text-xs text-gray-400 uppercase">
                  <tr>
                    <th className="px-6 py-3 text-left">File Name</th>
                    <th className="px-6 py-3 text-left">Type</th>
                    <th className="px-6 py-3 text-center">Size</th>
                    <th className="px-6 py-3 text-center">AI Risk Score</th>
                    <th className="px-6 py-3 text-center">Analysis Status</th>
                    <th className="px-6 py-3 text-center">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {audioFiles.map((audioFile) => (
                    <tr
                      key={audioFile.id}
                      onClick={() => setSelectedAudioFile(audioFile)}
                      className={`border-b border-[#21262d] hover:bg-[#161b22] cursor-pointer transition-colors ${
                        selectedAudioFile?.id === audioFile.id ? 'bg-[#161b22]' : 'bg-[#0D1117]'
                      }`}
                    >
                      <td className="px-6 py-4 font-medium text-white whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <FileAudio className="w-5 h-5 text-[var(--accent-teal)]" />
                          {audioFile.name}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className="text-xs font-medium text-gray-400">
                          {audioFile.type.split('/')[1].toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-center text-gray-400">
                        {formatFileSize(audioFile.size)}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskScoreColor(audioFile.riskScore)}`}>
                          {audioFile.riskScore}
                        </span>
                        {audioFile.analysis && (
                          <div className="mt-1">
                            <span className={`text-xs ${getConfidenceColor(audioFile.analysis.confidence)}`}>
                              {(audioFile.analysis.confidence * 100).toFixed(0)}% confidence
                            </span>
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 text-center">
                        {audioFile.isAnalyzed ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Analyzed
                          </span>
                        ) : isAnalyzing ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-500/20 text-yellow-400">
                            <div className="animate-spin rounded-full h-3 w-3 border-2 border-yellow-400 border-t-transparent mr-1"></div>
                            Analyzing...
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-500/20 text-gray-400">
                            <Info className="w-3 h-3 mr-1" />
                            Pending
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <div className="flex items-center gap-2">
                          <button 
                            onClick={(e) => {
                              e.stopPropagation()
                              if (audioFile.analysis) {
                                setAnalysisResult(audioFile.analysis)
                              } else {
                                analyzeAudioFile(audioFile)
                              }
                            }}
                            className="text-[var(--accent-teal)] hover:text-[var(--accent-teal)]/80 transition-colors text-xs"
                          >
                            {audioFile.analysis ? 'View Details' : 'Analyze'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Upload Section */}
          <div className="mt-6 bg-[#0D1117] rounded-lg border border-[#21262d] p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Upload New Audio File</h3>
            <div className="flex gap-4">
              <input
                type="file"
                accept="audio/*"
                onChange={handleFileUpload}
                className="flex-1 p-3 bg-[#161b22] border border-[#21262d] rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-[var(--accent-teal)]/20 file:text-[var(--accent-teal)] hover:file:bg-[var(--accent-teal)]/30"
              />
              <button
                onClick={isRecording ? stopRecording : startRecording}
                className={`flex items-center gap-2 px-4 py-3 rounded-lg font-semibold transition-colors ${
                  isRecording 
                    ? 'bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30' 
                    : 'bg-[var(--accent-teal)]/20 text-[var(--accent-teal)] border border-[var(--accent-teal)]/30 hover:bg-[var(--accent-teal)]/30'
                }`}
              >
                {isRecording ? (
                  <>
                    <Square className="w-4 h-4" />
                    Stop Recording
                  </>
                ) : (
                  <>
                    <Volume2 className="w-4 h-4" />
                    Record Audio
                  </>
                )}
              </button>
            </div>

            {selectedFile && (
              <div className="mt-4 p-3 bg-[#161b22] rounded-lg border border-[#21262d]">
                <p className="text-sm text-gray-400">
                  <strong>Selected file:</strong> {selectedFile.name} ({formatFileSize(selectedFile.size / 1024 / 1024)})
                </p>
                <button
                  onClick={handleAnalyzeAudio}
                  disabled={isAnalyzing}
                  className="mt-3 flex items-center gap-2 px-4 py-2 bg-[var(--accent-teal)]/20 text-[var(--accent-teal)] border border-[var(--accent-teal)]/30 rounded-lg hover:bg-[var(--accent-teal)]/30 transition-colors disabled:opacity-50"
                >
                  <Brain className="w-4 h-4" />
                  {isAnalyzing ? 'Analyzing...' : 'Analyze with AI'}
                </button>
              </div>
            )}

            {error && (
              <div className="mt-4 p-3 bg-red-500/20 border border-red-500/30 rounded-lg">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-400" />
                  <span className="text-red-400 text-sm">{error}</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Analysis Results Panel */}
        {(analysisResult || selectedAudioFile?.analysis) && (
          <div className="w-96 bg-[#010409] border-l border-[#21262d] p-6 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold">Analysis Results</h3>
              <button
                onClick={() => {
                  setAnalysisResult(null)
                  setSelectedAudioFile(null)
                }}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            <div className="flex-1 bg-[#0D1117] rounded-lg p-4 border border-[#21262d]">
              {(() => {
                const result = analysisResult || selectedAudioFile?.analysis
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
                          {result.triggers.map((trigger, index) => (
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