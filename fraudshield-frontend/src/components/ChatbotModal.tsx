'use client'

import { useState, useRef, useEffect } from 'react'
import { XMarkIcon, PaperAirplaneIcon, ChatBubbleLeftRightIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import { apiService, getRiskLevelColor, getConfidenceColor } from '@/services/api'
import { AnalysisResponse, EmailAnalysisResponse, ChatAnalysisResponse, ApiError } from '@/types/analysis'
import AnalysisModal from './AnalysisModal'
import TypingAnimation from './TypingAnimation'

interface ChatMessage {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: Date
  analysis?: AnalysisResponse | EmailAnalysisResponse | ChatAnalysisResponse
  isAnalyzing?: boolean
  isTyping?: boolean
  fullContent?: string
}

interface ChatbotModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function ChatbotModal({ isOpen, onClose }: ChatbotModalProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [senderInfo, setSenderInfo] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisResponse | EmailAnalysisResponse | ChatAnalysisResponse | null>(null)
  const [showAnalysisModal, setShowAnalysisModal] = useState(false)
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [detectedType, setDetectedType] = useState<'sms' | 'email' | 'chat' | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isOpen) {
      checkBackendStatus()
    }
  }, [isOpen])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const checkBackendStatus = async () => {
    try {
      await apiService.healthCheck()
      setBackendStatus('online')
    } catch (error) {
      setBackendStatus('offline')
    }
  }

  const generateUniqueId = () => {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  const addAIMessage = (content: string, analysis?: AnalysisResponse | EmailAnalysisResponse | ChatAnalysisResponse, isTyping: boolean = false) => {
    const newMessage: ChatMessage = {
      id: generateUniqueId(),
      type: 'ai',
      content: isTyping ? '' : content,
      fullContent: content,
      timestamp: new Date(),
      analysis,
      isTyping
    }
    setMessages(prev => [...prev, newMessage])
  }

  const addUserMessage = (content: string) => {
    const newMessage: ChatMessage = {
      id: generateUniqueId(),
      type: 'user',
      content,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, newMessage])
  }

  const handleAnalyze = async () => {
    if (!inputValue.trim() || isAnalyzing) return

    const content = inputValue.trim()
    addUserMessage(content)
    setInputValue('')
    setIsAnalyzing(true)

    try {
      // Use unified analysis that automatically detects content type
      const analysis = await apiService.analyzeUnified(content, senderInfo)
      
      // Store the detected type for display
      setDetectedType(analysis.detected_type)

      // Create clean AI response using Gemini explanation if available
      let aiResponse = ''
      
      if (analysis.gemini_explanation) {
        // Use Gemini detailed explanation for comprehensive response
        const gemini = analysis.gemini_explanation
        
        let nextStepsText = ''
        if (gemini.next_steps) {
          nextStepsText = `\n\nNext Steps:\nImmediate: ${gemini.next_steps.immediate}\nShort-term: ${gemini.next_steps.short_term}\nLong-term: ${gemini.next_steps.long_term}`
        }
        
        aiResponse = `${gemini.detailed_explanation}\n\nTechnical Insights: ${gemini.technical_insights}\n\nConfidence Assessment: ${gemini.confidence_assessment}${nextStepsText}\n\nThis message was detected as ${analysis.detected_type.toUpperCase()} with ${analysis.risk_level} risk (${(analysis.risk_score * 100).toFixed(1)}% confidence: ${(analysis.confidence * 100).toFixed(1)}%). Click "View Details" for full analysis.`
      } else {
        // Fallback to basic explanation if Gemini explanation not available
        aiResponse = `Analysis complete: ${analysis.detected_type.toUpperCase()} content shows ${analysis.risk_level} risk (${(analysis.risk_score * 100).toFixed(1)}% confidence: ${(analysis.confidence * 100).toFixed(1)}%). Fraud detected: ${analysis.is_fraud ? 'YES' : 'NO'}. Click "View Details" for full analysis.`
      }

      // Add AI message with typing animation
      addAIMessage(aiResponse, analysis, true)

    } catch (error) {
      console.error('Analysis failed:', error)
      
      let errorMessage = "Analysis failed. "
      
      if (error && typeof error === 'object' && 'status' in error) {
        const apiError = error as ApiError
        errorMessage += `${apiError.message}. `
        if (apiError.status === 503) {
          errorMessage += "Backend service is not ready. Please try again in a moment."
        } else if (apiError.status >= 500) {
          errorMessage += "Server error occurred. Please try again."
        } else {
          errorMessage += "Request failed. Please check your input and try again."
        }
      } else {
        errorMessage += "Unable to connect to the analysis service. Please check if the backend is running on http://localhost:8000"
      }

      addAIMessage(errorMessage)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleAnalyze()
    }
  }

  const handleViewDetails = (analysis: AnalysisResponse | EmailAnalysisResponse | ChatAnalysisResponse) => {
    setSelectedAnalysis(analysis)
    setShowAnalysisModal(true)
  }

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'sms': return '📱'
      case 'email': return '📧'
      case 'chat': return '💬'
      default: return '📝'
    }
  }

  const getChannelColor = (channel: string) => {
    switch (channel) {
      case 'sms': return 'text-blue-400'
      case 'email': return 'text-green-400'
      case 'chat': return 'text-purple-400'
      default: return 'text-gray-400'
    }
  }

  if (!isOpen) return null

  return (
    <>
      <div className="fixed inset-0 bg-black/50 flex items-start justify-end z-50">
        <div className="bg-[#010409] border-l border-[#21262d] w-1/2 h-full flex flex-col shadow-2xl">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-[#21262d]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-[var(--accent-teal)]/20 to-[var(--accent-teal)]/10 border border-[var(--accent-teal)]/30 flex items-center justify-center">
                <ChatBubbleLeftRightIcon className="w-6 h-6 text-[var(--accent-teal)]" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">AI Fraud Detection Assistant</h3>
                <div className="flex items-center gap-2">
                  <p className="text-sm text-gray-400">Detect fraud in SMS, Email, and Chat messages</p>
                  <div className={`w-2 h-2 rounded-full ${
                    backendStatus === 'online' ? 'bg-green-400' :
                    backendStatus === 'offline' ? 'bg-red-400' :
                    'bg-yellow-400 animate-pulse'
                  }`} />
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-[#21262d] rounded-lg"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>

          {/* Sender Info Input */}
          <div className="p-4 border-b border-[#21262d]">
            <input
              type="text"
              placeholder="Sender info (optional) - email, phone, username, etc."
              value={senderInfo}
              onChange={(e) => setSenderInfo(e.target.value)}
              className="w-full px-3 py-2 bg-[#0D1117] border border-[#21262d] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[var(--accent-teal)] text-sm"
            />
          </div>

          {/* Messages Area */}
          <div className="flex-1 p-6 overflow-y-auto space-y-4 scrollbar-thin scrollbar-thumb-transparent scrollbar-track-transparent" style={{ scrollbarWidth: 'thin', scrollbarColor: 'transparent transparent' }}>
            {messages.length === 0 && (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-r from-[var(--accent-teal)]/20 to-[var(--accent-teal)]/10 border border-[var(--accent-teal)]/30 flex items-center justify-center mx-auto mb-4">
                    <ChatBubbleLeftRightIcon className="w-8 h-8 text-[var(--accent-teal)]" />
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-2">AI Fraud Detection</h3>
                  <p className="text-gray-400 text-lg">Analyze SMS, Email, and Chat messages for fraud and scam indicators</p>
                </div>
              </div>
            )}
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start gap-3 ${
                  message.type === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.type === 'ai' && (
                  <div className="w-8 h-8 rounded-full bg-[var(--accent-teal)]/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-[var(--accent-teal)] font-bold text-sm">AI</span>
                  </div>
                )}
                
                <div className={`max-w-[80%] ${
                  message.type === 'user' ? 'order-first' : ''
                }`}>
                  <div className={`rounded-lg p-4 ${
                    message.type === 'user'
                      ? 'bg-[var(--accent-teal)]/10 border border-[var(--accent-teal)]/30'
                      : 'bg-[#0D1117] border border-[#21262d]'
                  }`}>
                    <div className="flex items-center gap-2 mb-2">
                      {message.type === 'ai' && message.analysis && 'detected_type' in message.analysis && (
                        <span className={`text-sm ${getChannelColor(message.analysis.detected_type as string)}`}>
                          {getChannelIcon(message.analysis.detected_type as string)} {(message.analysis.detected_type as string).toUpperCase()}
                        </span>
                      )}
                      <span className="text-xs text-gray-500">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    
                    <div className="text-gray-300 whitespace-pre-wrap">
                      {message.isTyping ? (
                        <TypingAnimation 
                          text={message.fullContent || message.content}
                          speed={20}
                          onComplete={() => {
                            // Mark typing as complete
                            setMessages(prev => prev.map(msg => 
                              msg.id === message.id 
                                ? { ...msg, isTyping: false, content: msg.fullContent || msg.content }
                                : msg
                            ))
                          }}
                        />
                      ) : (
                        message.content
                      )}
                    </div>
                    
                    {message.analysis && (
                      <div className="mt-3 pt-3 border-t border-[#21262d]">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className={`text-sm font-medium ${getRiskLevelColor(message.analysis.risk_level).split(' ')[1]}`}>
                              {message.analysis.risk_level} Risk
                            </span>
                            <span className={`text-sm ${getConfidenceColor(message.analysis.confidence)}`}>
                              {(message.analysis.confidence * 100).toFixed(0)}% confidence
                            </span>
                          </div>
                          <button
                            onClick={() => handleViewDetails(message.analysis!)}
                            className="text-[var(--accent-teal)] hover:text-[var(--accent-teal)]/80 text-sm font-medium transition-colors"
                          >
                            View Details →
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {message.type === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-[var(--accent-teal)]/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-[var(--accent-teal)] font-bold text-sm">U</span>
                  </div>
                )}
              </div>
            ))}
            
            {isAnalyzing && (
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-[var(--accent-teal)]/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-[var(--accent-teal)] font-bold text-sm">AI</span>
                </div>
                <div className="bg-[#0D1117] border border-[#21262d] rounded-lg p-4">
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-[var(--accent-teal)] border-t-transparent"></div>
                    <span className="text-gray-400">Analyzing message...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-6 border-t border-[#21262d]">
            <div className="flex gap-3">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Paste any SMS, Email, or Chat content here for fraud detection analysis..."
                className="flex-1 min-h-[60px] p-3 bg-[#0D1117] border border-[#21262d] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[var(--accent-teal)] resize-none"
                disabled={isAnalyzing}
              />
              <button
                onClick={handleAnalyze}
                disabled={!inputValue.trim() || isAnalyzing}
                className="px-4 py-2 bg-[var(--accent-teal)]/10 border border-[var(--accent-teal)] text-[var(--accent-teal)] rounded-lg hover:bg-[var(--accent-teal)]/20 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <PaperAirplaneIcon className="w-4 h-4" />
                Analyze
              </button>
            </div>
            
            {backendStatus === 'offline' && (
              <div className="mt-3 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                <div className="flex items-center gap-2">
                  <ExclamationTriangleIcon className="w-4 h-4 text-red-400" />
                  <span className="text-red-400 text-sm">
                    Backend is offline. Please ensure the Python FastAPI service is running on http://localhost:8000
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Analysis Modal */}
      {showAnalysisModal && selectedAnalysis && (
        <AnalysisModal
          isOpen={showAnalysisModal}
          onClose={() => setShowAnalysisModal(false)}
          analysis={selectedAnalysis}
          messageType={detectedType || 'sms'}
        />
      )}
    </>
  )
}
