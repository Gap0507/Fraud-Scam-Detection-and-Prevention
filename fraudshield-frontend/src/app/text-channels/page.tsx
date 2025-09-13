'use client'

import { useState, useEffect } from 'react'
import { MagnifyingGlassIcon, PlusIcon, ChatBubbleLeftRightIcon, XMarkIcon, ExclamationTriangleIcon, CheckCircleIcon, InformationCircleIcon } from '@heroicons/react/24/outline'
import MainLayout from '@/components/MainLayout'
import ChatbotModal from '@/components/ChatbotModal'
import AnalysisModal from '@/components/AnalysisModal'
import { apiService, checkBackendHealth, getRiskLevelColor, getConfidenceColor } from '@/services/api'
import { Message, AnalysisResponse, EmailAnalysisResponse, ChatAnalysisResponse, ApiError } from '@/types/analysis'

type TabType = 'sms' | 'chat' | 'email'

export default function TextChannelsPage() {
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null)
  const [activeTab, setActiveTab] = useState<TabType>('sms')
  const [isChatbotOpen, setIsChatbotOpen] = useState(false)
  const [showAnalysisModal, setShowAnalysisModal] = useState(false)
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisResponse | EmailAnalysisResponse | ChatAnalysisResponse | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [searchQuery, setSearchQuery] = useState('')
  const [messages, setMessages] = useState<Message[]>([])

  // Demo messages data for initial load
  const demoMessages: Message[] = [
    // SMS Messages
    {
      id: '1',
      sender: '+1 (555) 123-4567',
      preview: 'Urgent: Your account has been compromised...',
      riskScore: 'HIGH',
      timestamp: '1 hour ago',
      content: 'Urgent: Your account has been compromised. Please click the link immediately to secure your account: https://fake-bank-security.com/verify',
      suspiciousKeywords: ['urgent', 'compromised', 'click immediately', 'secure account'],
      type: 'sms'
    },
    {
      id: '2',
      sender: '+1 (555) 987-6543',
      preview: 'Hi Sarah, just checking in on our meeting...',
      riskScore: 'LOW',
      timestamp: '2 hours ago',
      content: 'Hi Sarah, just checking in on our meeting tomorrow at 2 PM. Looking forward to discussing the project updates.',
      suspiciousKeywords: [],
      type: 'sms'
    },
    {
      id: '3',
      sender: '+1 (555) 246-8012',
      preview: 'Congratulations! You\'ve won a free vacation...',
      riskScore: 'HIGH',
      timestamp: '3 hours ago',
      content: 'Congratulations! You\'ve won a free vacation to Hawaii! Click here to claim your prize: https://fake-prize.com/claim-now',
      suspiciousKeywords: ['congratulations', 'won', 'free vacation', 'click here', 'claim prize'],
      type: 'sms'
    },
    {
      id: '4',
      sender: '+1 (555) 369-1470',
      preview: 'Your package is delayed. Please update your...',
      riskScore: 'MEDIUM',
      timestamp: '2 hours ago',
      content: 'Your package is delayed. Please update your delivery address by clicking the link below to avoid cancellation. hXXps://bit[.]ly/fakepackage-update We apologize for the inconvenience.',
      suspiciousKeywords: ['delayed', 'update', 'clicking the link', 'cancellation'],
      type: 'sms'
    },
    {
      id: '5',
      sender: '+1 (555) 482-9630',
      preview: 'Reminder: Your appointment with Dr. Smith...',
      riskScore: 'LOW',
      timestamp: '4 hours ago',
      content: 'Reminder: Your appointment with Dr. Smith is scheduled for tomorrow at 10 AM. Please arrive 15 minutes early.',
      suspiciousKeywords: [],
      type: 'sms'
    },
    {
      id: '6',
      sender: '+1 (555) 505-7890',
      preview: 'Your bank requires verification. Please provide...',
      riskScore: 'HIGH',
      timestamp: '5 hours ago',
      content: 'Your bank requires verification. Please provide your account details and social security number immediately to avoid account suspension.',
      suspiciousKeywords: ['bank', 'verification', 'account details', 'social security', 'immediately', 'suspension'],
      type: 'sms'
    },
    // Chat Messages
    {
      id: '7',
      sender: 'john_doe_2024',
      preview: 'Hey! I have an amazing investment opportunity...',
      riskScore: 'HIGH',
      timestamp: '30 minutes ago',
      content: 'Hey! I have an amazing investment opportunity that can make you rich in just 30 days! Join our exclusive group now: https://fake-crypto-investment.com/join',
      suspiciousKeywords: ['investment opportunity', 'make you rich', '30 days', 'exclusive group'],
      type: 'chat'
    },
    {
      id: '8',
      sender: 'sarah_wilson',
      preview: 'Thanks for the help with the project...',
      riskScore: 'LOW',
      timestamp: '1 hour ago',
      content: 'Thanks for the help with the project yesterday. The presentation went really well!',
      suspiciousKeywords: [],
      type: 'chat'
    },
    {
      id: '9',
      sender: 'crypto_trader_pro',
      preview: 'URGENT: Your wallet is at risk! Click here...',
      riskScore: 'HIGH',
      timestamp: '2 hours ago',
      content: 'URGENT: Your wallet is at risk! Click here immediately to secure your funds: https://fake-wallet-security.com/verify-now',
      suspiciousKeywords: ['urgent', 'wallet', 'at risk', 'click here', 'immediately', 'secure funds'],
      type: 'chat'
    },
    // Email Messages
    {
      id: '10',
      sender: 'noreply@bank-security.com',
      preview: 'Security Alert: Unusual Activity Detected',
      riskScore: 'HIGH',
      timestamp: '45 minutes ago',
      content: 'Dear Customer,\n\nWe have detected unusual activity on your account. Please verify your identity by clicking the link below:\n\nhttps://fake-bank-verification.com/verify\n\nIf you do not take action within 24 hours, your account will be suspended.\n\nBest regards,\nSecurity Team',
      suspiciousKeywords: ['unusual activity', 'verify your identity', 'click the link', 'account will be suspended'],
      type: 'email'
    },
    {
      id: '11',
      sender: 'support@company.com',
      preview: 'Your order has been shipped',
      riskScore: 'LOW',
      timestamp: '3 hours ago',
      content: 'Hello,\n\nYour order #12345 has been shipped and is on its way to you. You can track your package using the tracking number: 1Z999AA1234567890\n\nThank you for your business!\n\nCustomer Service Team',
      suspiciousKeywords: [],
      type: 'email'
    },
    {
      id: '12',
      sender: 'winner@lottery-prize.org',
      preview: 'Congratulations! You\'ve Won $1,000,000!',
      riskScore: 'HIGH',
      timestamp: '4 hours ago',
      content: 'Congratulations!\n\nYou have been selected as the winner of our $1,000,000 lottery prize! To claim your winnings, please provide your personal information and bank details by clicking here:\n\nhttps://fake-lottery-claim.com/winner\n\nThis offer expires in 48 hours.\n\nLottery Prize Committee',
      suspiciousKeywords: ['congratulations', 'winner', 'lottery prize', 'personal information', 'bank details', 'expires'],
      type: 'email'
    }
  ]

  // Initialize messages and check backend status
  useEffect(() => {
    setMessages(demoMessages)
    checkBackendStatus()
  }, [])

  const checkBackendStatus = async () => {
    setBackendStatus('checking')
    const isOnline = await checkBackendHealth()
    setBackendStatus(isOnline ? 'online' : 'offline')
  }

  const analyzeMessage = async (message: Message) => {
    if (message.isAnalyzed || isAnalyzing) return

    setIsAnalyzing(true)
    try {
      // Use unified analysis that automatically detects content type
      const analysis = await apiService.analyzeUnified(message.content, message.sender)

      // Update message with analysis
      setMessages(prev => prev.map(m => 
        m.id === message.id 
          ? { 
              ...m, 
              analysis, 
              isAnalyzed: true,
              riskScore: analysis.risk_level,
              suspiciousKeywords: analysis.triggers,
              type: analysis.detected_type as 'sms' | 'email' | 'chat'
            }
          : m
      ))

    } catch (error) {
      console.error('Analysis failed:', error)
      // You could show a toast notification here
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleViewDetails = (message: Message) => {
    if (message.analysis) {
      setSelectedAnalysis(message.analysis)
      setShowAnalysisModal(true)
    } else {
      // Analyze first, then show details
      analyzeMessage(message)
    }
  }

  const handleMarkAsSafe = (message: Message) => {
    setMessages(prev => prev.map(m => 
      m.id === message.id 
        ? { ...m, riskScore: 'LOW' as const, isAnalyzed: true }
        : m
    ))
  }

  const handleQuarantine = (message: Message) => {
    setMessages(prev => prev.map(m => 
      m.id === message.id 
        ? { ...m, riskScore: 'HIGH' as const, isAnalyzed: true }
        : m
    ))
  }

  // Filter messages based on active tab and search query
  const filteredMessages = messages.filter(message => {
    const matchesTab = message.type === activeTab
    const matchesSearch = searchQuery === '' || 
      message.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      message.sender.toLowerCase().includes(searchQuery.toLowerCase()) ||
      message.preview.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesTab && matchesSearch
  })

  // Get message counts for each type
  const messageCounts = {
    sms: messages.filter(m => m.type === 'sms').length,
    email: messages.filter(m => m.type === 'email').length,
    chat: messages.filter(m => m.type === 'chat').length
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

  const getChannelColor = (channel: string) => {
    switch (channel) {
      case 'sms': return 'text-blue-400'
      case 'email': return 'text-green-400'
      case 'chat': return 'text-purple-400'
      default: return 'text-gray-400'
    }
  }

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'sms': return '📱'
      case 'email': return '📧'
      case 'chat': return '💬'
      default: return '📝'
    }
  }

  return (
    <MainLayout>
      {/* Header */}
      <header className="flex items-center justify-between p-6 border-b border-[#21262d]">
        <div>
          <h2 className="text-3xl font-bold">Text Channels</h2>
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
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setIsChatbotOpen(true)}
            className="group flex items-center justify-center w-12 h-10 bg-gradient-to-r from-[var(--accent-teal)]/20 to-[var(--accent-teal)]/10 border border-[var(--accent-teal)]/30 rounded-lg text-[var(--accent-teal)] hover:from-[var(--accent-teal)]/30 hover:to-[var(--accent-teal)]/20 hover:border-[var(--accent-teal)] hover:shadow-lg hover:shadow-[var(--accent-teal)]/20 transition-all duration-300 relative overflow-hidden"
            title="AI Chat Assistant - Click to get help with fraud detection"
          >
            <ChatBubbleLeftRightIcon className="w-5 h-5 relative z-10" />
            <div className="absolute inset-0 bg-gradient-to-r from-[var(--accent-teal)]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-[var(--accent-teal)]/10 border border-[var(--accent-teal)] text-[var(--accent-teal)] rounded-lg hover:bg-[var(--accent-teal)]/20 transition-colors">
            <PlusIcon className="w-5 h-5" />
            New Message
          </button>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="border-b border-[#21262d]">
        <nav className="flex space-x-8 px-6">
          {[
            { id: 'sms', label: 'SMS', icon: '📱', count: messages.filter(m => m.type === 'sms').length },
            { id: 'chat', label: 'Chat', icon: '💬', count: messages.filter(m => m.type === 'chat').length },
            { id: 'email', label: 'Email', icon: '📧', count: messages.filter(m => m.type === 'email').length }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-[var(--accent-teal)] text-[var(--accent-teal)]'
                  : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
              }`}
            >
              <span className="flex items-center gap-2">
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </span>
              <span className={`ml-2 py-0.5 px-2 rounded-full text-xs ${
                activeTab === tab.id
                  ? 'bg-[var(--accent-teal)]/20 text-[var(--accent-teal)]'
                  : 'bg-gray-600/20 text-gray-400'
              }`}>
                {tab.count}
              </span>
            </button>
          ))}
        </nav>
      </div>

      {/* Content Area */}
      <div className="flex-1 flex">
        {/* Messages List */}
        <div className="flex-1 p-6">
          <div className="bg-[#0D1117] rounded-lg border border-[#21262d] overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-[#161b22] text-xs text-gray-400 uppercase">
                  <tr>
                    <th className="px-6 py-3 text-left">Sender</th>
                    <th className="px-6 py-3 text-left">Message Preview</th>
                    <th className="px-6 py-3 text-center">Type</th>
                    <th className="px-6 py-3 text-center">AI Risk Score</th>
                    <th className="px-6 py-3 text-center">Analysis Status</th>
                    <th className="px-6 py-3 text-center">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredMessages.map((message) => (
                    <tr
                      key={message.id}
                      onClick={() => setSelectedMessage(message)}
                      className={`border-b border-[#21262d] hover:bg-[#161b22] cursor-pointer transition-colors ${
                        selectedMessage?.id === message.id ? 'bg-[#161b22]' : 'bg-[#0D1117]'
                      }`}
                    >
                      <td className="px-6 py-4 font-medium text-white whitespace-nowrap">
                        {message.sender}
                      </td>
                      <td className="px-6 py-4 text-gray-400">
                        {message.preview}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <div className="flex items-center justify-center gap-2">
                          <span className={`text-lg ${getChannelColor(message.type)}`}>
                            {getChannelIcon(message.type)}
                          </span>
                          <span className={`text-xs font-medium ${getChannelColor(message.type)}`}>
                            {message.type.toUpperCase()}
                          </span>
                          {message.analysis && 'detection_confidence' in message.analysis && (
                            <span className="text-xs text-gray-500">
                              ({(message.analysis.detection_confidence as number * 100).toFixed(0)}%)
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskScoreColor(message.riskScore)}`}>
                          {message.riskScore}
                        </span>
                        {message.analysis && (
                          <div className="mt-1">
                            <span className={`text-xs ${getConfidenceColor(message.analysis.confidence)}`}>
                              {(message.analysis.confidence * 100).toFixed(0)}% confidence
                            </span>
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 text-center">
                        {message.isAnalyzed ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400">
                            <CheckCircleIcon className="w-3 h-3 mr-1" />
                            Analyzed
                          </span>
                        ) : isAnalyzing ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-500/20 text-yellow-400">
                            <div className="animate-spin rounded-full h-3 w-3 border-2 border-yellow-400 border-t-transparent mr-1"></div>
                            Analyzing...
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-500/20 text-gray-400">
                            <InformationCircleIcon className="w-3 h-3 mr-1" />
                            Pending
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <div className="flex items-center gap-2">
                          <button 
                            onClick={(e) => {
                              e.stopPropagation()
                              handleViewDetails(message)
                            }}
                            className="text-[var(--accent-teal)] hover:text-[var(--accent-teal)]/80 transition-colors text-xs"
                          >
                            {message.analysis ? 'View Details' : 'Analyze'}
                          </button>
                          {message.analysis && (
                            <>
                              <button 
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleMarkAsSafe(message)
                                }}
                                className="text-green-400 hover:text-green-300 transition-colors text-xs"
                              >
                                Mark Safe
                              </button>
                              <button 
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleQuarantine(message)
                                }}
                                className="text-red-400 hover:text-red-300 transition-colors text-xs"
                              >
                                Quarantine
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Message Details Panel */}
        {selectedMessage && (
          <div className="w-96 bg-[#010409] border-l border-[#21262d] p-6 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold">Message Details</h3>
              <button
                onClick={() => setSelectedMessage(null)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            <div className="flex-1 bg-[#0D1117] rounded-lg p-4 border border-[#21262d]">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-[var(--accent-teal)] flex items-center justify-center text-white font-bold text-lg">
                  {selectedMessage.type.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1">
                  <p className="text-white font-semibold">{selectedMessage.sender}</p>
                  <p className="text-gray-400 text-xs">
                    {selectedMessage.type.toUpperCase()} Received: {selectedMessage.timestamp}
                  </p>
                </div>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskScoreColor(selectedMessage.riskScore)}`}>
                  {selectedMessage.riskScore}
                </span>
              </div>

              <div className="text-gray-300 space-y-4 mb-6">
                <p className="whitespace-pre-wrap">{selectedMessage.content}</p>
              </div>

              {selectedMessage.suspiciousKeywords.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-white font-semibold mb-2">Suspicious Keywords</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedMessage.suspiciousKeywords.map((keyword, index) => (
                      <span
                        key={index}
                        className="bg-red-500/20 text-red-400 text-xs font-medium px-2 py-1 rounded-full"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {selectedMessage.analysis && (
              <div className="mb-4 p-3 bg-[#161b22] rounded-lg border border-[#21262d]">
                <h4 className="text-white font-semibold mb-2">AI Analysis Results</h4>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-gray-400">Risk Score:</span>
                    <span className={`ml-2 font-medium ${getRiskLevelColor(selectedMessage.analysis.risk_level).split(' ')[1]}`}>
                      {(selectedMessage.analysis.risk_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Confidence:</span>
                    <span className={`ml-2 font-medium ${getConfidenceColor(selectedMessage.analysis.confidence)}`}>
                      {(selectedMessage.analysis.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Processing Time:</span>
                    <span className="ml-2 text-white font-medium">
                      {(selectedMessage.analysis.processing_time * 1000).toFixed(0)}ms
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Analysis ID:</span>
                    <span className="ml-2 text-white font-mono text-xs">
                      {selectedMessage.analysis.analysis_id}
                    </span>
                  </div>
                </div>
                <p className="text-gray-300 text-sm mt-2">{selectedMessage.analysis.explanation}</p>
              </div>
            )}

            <div className="mt-4 flex gap-2">
              <button 
                onClick={() => handleMarkAsSafe(selectedMessage)}
                className="flex-1 bg-green-600/20 text-green-400 border border-green-600 rounded-md py-2 text-sm font-semibold hover:bg-green-600/30 transition-colors"
              >
                Mark as Safe
              </button>
              <button 
                onClick={() => handleQuarantine(selectedMessage)}
                className="flex-1 bg-red-600/20 text-red-400 border border-red-600 rounded-md py-2 text-sm font-semibold hover:bg-red-600/30 transition-colors"
              >
                Quarantine
              </button>
              {selectedMessage.analysis && (
                <button 
                  onClick={() => {
                    setSelectedAnalysis(selectedMessage.analysis!)
                    setShowAnalysisModal(true)
                  }}
                  className="flex-1 bg-[var(--accent-teal)]/20 text-[var(--accent-teal)] border border-[var(--accent-teal)] rounded-md py-2 text-sm font-semibold hover:bg-[var(--accent-teal)]/30 transition-colors"
                >
                  Full Analysis
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Enhanced Chatbot Modal */}
      <ChatbotModal 
        isOpen={isChatbotOpen} 
        onClose={() => setIsChatbotOpen(false)} 
      />

      {/* Analysis Modal */}
      {showAnalysisModal && selectedAnalysis && (
        <AnalysisModal
          isOpen={showAnalysisModal}
          onClose={() => setShowAnalysisModal(false)}
          analysis={selectedAnalysis}
          messageType={activeTab}
        />
      )}
    </MainLayout>
  )
}