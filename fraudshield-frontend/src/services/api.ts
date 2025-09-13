// API service layer for FastAPI backend integration

import { 
  AnalysisRequest, 
  AnalysisResponse, 
  EmailAnalysisRequest, 
  EmailAnalysisResponse, 
  ChatAnalysisRequest, 
  ChatAnalysisResponse,
  AudioAnalysisResponse,
  ApiError 
} from '@/types/analysis'

const API_BASE_URL = 'http://localhost:8000'

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`
    let errorDetails: string | undefined

    try {
      const errorData = await response.json()
      errorMessage = errorData.detail || errorData.error || errorMessage
      errorDetails = errorData.detail
    } catch {
      // If response is not JSON, use the status text
    }

    const error = new Error(errorMessage) as ApiError
    error.status = response.status
    error.details = errorDetails
    throw error
  }

  return response.json()
}

export const apiService = {
  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await fetch(`${API_BASE_URL}/health`)
    return handleResponse(response)
  },

  // Analyze text (SMS, Chat)
  async analyzeText(request: AnalysisRequest): Promise<AnalysisResponse> {
    const response = await fetch(`${API_BASE_URL}/analyze/text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })
    return handleResponse(response)
  },

  // Analyze email
  async analyzeEmail(request: EmailAnalysisRequest): Promise<EmailAnalysisResponse> {
    const response = await fetch(`${API_BASE_URL}/analyze/email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })
    return handleResponse(response)
  },

  // Analyze chat
  async analyzeChat(request: ChatAnalysisRequest): Promise<ChatAnalysisResponse> {
    const response = await fetch(`${API_BASE_URL}/analyze/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })
    return handleResponse(response)
  },

  // Old audio analyzer removed - using only Gemini now

  // Analyze audio with Gemini
  async analyzeAudioGemini(audioFile: File): Promise<AudioAnalysisResponse> {
    const formData = new FormData()
    formData.append('audio_file', audioFile)

    const response = await fetch(`${API_BASE_URL}/analyze/audio/gemini`, {
      method: 'POST',
      body: formData,
    })
    return handleResponse(response)
  },

  // Analyze video with Gemini
  async analyzeVideoGemini(videoFile: File): Promise<any> {
    const formData = new FormData()
    formData.append('video_file', videoFile)

    const response = await fetch(`${API_BASE_URL}/analyze/video/gemini`, {
      method: 'POST',
      body: formData,
    })
    return handleResponse(response)
  },

  // Comparison removed - using only Gemini now

  // Transcription removed - using only Gemini now

  // Get model status
  async getModelStatus(): Promise<{
    text_analyzer: { ready: boolean; model_name: string }
    sms_analyzer: { ready: boolean; model_name: string }
    email_analyzer: { ready: boolean; model_name: string }
    chat_analyzer: { ready: boolean; model_name: string }
    audio_analyzer: { ready: boolean; model_name: string }
    voice_analyzer: { ready: boolean; model_name: string }
    video_analyzer: { ready: boolean; model_name: string }
  }> {
    const response = await fetch(`${API_BASE_URL}/models/status`)
    return handleResponse(response)
  },

  // Generate simulated data
  async generateSimulatedData(count: number = 10, channel: string = 'sms'): Promise<{
    message: string
    data: any[]
    timestamp: string
  }> {
    const response = await fetch(`${API_BASE_URL}/simulate/data?count=${count}&channel=${channel}`)
    return handleResponse(response)
  },

  // Unified analysis - automatically detects content type
  async analyzeUnified(content: string, senderInfo?: string): Promise<AnalysisResponse & {
    detected_type: 'sms' | 'email' | 'chat'
    unified_analysis: boolean
    detection_confidence: number
  }> {
    const response = await fetch(`${API_BASE_URL}/analyze/unified`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content,
        sender_info: senderInfo || ''
      }),
    })
    return handleResponse(response)
  }
}

// Utility function to check if backend is available
export async function checkBackendHealth(): Promise<boolean> {
  try {
    await apiService.healthCheck()
    return true
  } catch (error) {
    console.error('Backend health check failed:', error)
    return false
  }
}

// Utility function to get risk level color
export function getRiskLevelColor(riskLevel: 'LOW' | 'MEDIUM' | 'HIGH'): string {
  switch (riskLevel) {
    case 'HIGH':
      return 'bg-red-500/20 text-red-400 border-red-500/30'
    case 'MEDIUM':
      return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
    case 'LOW':
      return 'bg-green-500/20 text-green-400 border-green-500/30'
    default:
      return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
  }
}

// Utility function to get confidence color
export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'text-green-400'
  if (confidence >= 0.6) return 'text-yellow-400'
  return 'text-red-400'
}

// Export individual functions for easier imports
export const { 
  healthCheck, 
  analyzeText, 
  analyzeEmail, 
  analyzeChat, 
  analyzeAudioGemini,
  analyzeVideoGemini,
  getModelStatus, 
  generateSimulatedData, 
  analyzeUnified 
} = apiService

