'use client'

import { XMarkIcon, ExclamationTriangleIcon, CheckCircleIcon, InformationCircleIcon } from '@heroicons/react/24/outline'
import { AnalysisResponse, EmailAnalysisResponse, ChatAnalysisResponse } from '@/types/analysis'
import { getRiskLevelColor, getConfidenceColor } from '@/services/api'

interface AnalysisModalProps {
  isOpen: boolean
  onClose: () => void
  analysis: AnalysisResponse | EmailAnalysisResponse | ChatAnalysisResponse
  messageType: 'sms' | 'email' | 'chat'
}

export default function AnalysisModal({ isOpen, onClose, analysis, messageType }: AnalysisModalProps) {

  if (!isOpen) return null

  const isEmail = 'subject' in analysis
  const isChat = 'messages' in analysis

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case 'HIGH':
        return <ExclamationTriangleIcon className="w-6 h-6 text-red-400" />
      case 'MEDIUM':
        return <ExclamationTriangleIcon className="w-6 h-6 text-yellow-400" />
      case 'LOW':
        return <CheckCircleIcon className="w-6 h-6 text-green-400" />
      default:
        return <InformationCircleIcon className="w-6 h-6 text-gray-400" />
    }
  }

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Risk Assessment */}
      <div className="bg-[#0D1117] rounded-lg p-4 border border-[#21262d]">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          {getRiskIcon(analysis.risk_level)}
          Risk Assessment
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-400">Risk Level</p>
            <p className={`text-lg font-bold ${getRiskLevelColor(analysis.risk_level).split(' ')[1]}`}>
              {analysis.risk_level}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Risk Score</p>
            <p className="text-lg font-bold text-white">
              {(analysis.risk_score * 100).toFixed(1)}%
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Confidence</p>
            <p className={`text-lg font-bold ${getConfidenceColor(analysis.confidence)}`}>
              {(analysis.confidence * 100).toFixed(1)}%
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Processing Time</p>
            <p className="text-lg font-bold text-white">
              {(analysis.processing_time * 1000).toFixed(0)}ms
            </p>
          </div>
        </div>
      </div>

      {/* AI Explanation */}
      <div className="bg-[#0D1117] rounded-lg p-4 border border-[#21262d]">
        <h3 className="text-lg font-semibold text-white mb-3">AI Analysis</h3>
        <p className="text-gray-300 leading-relaxed">{analysis.explanation}</p>
      </div>

      {/* Triggers */}
      {analysis.triggers.length > 0 && (
        <div className="bg-[#0D1117] rounded-lg p-4 border border-[#21262d]">
          <h3 className="text-lg font-semibold text-white mb-3">Trigger Phrases</h3>
          <div className="flex flex-wrap gap-2">
            {analysis.triggers.map((trigger, index) => (
              <span
                key={index}
                className="bg-red-500/20 text-red-400 text-sm font-medium px-3 py-1 rounded-full border border-red-500/30"
              >
                {trigger}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Email-specific content */}
      {isEmail && (
        <div className="bg-[#0D1117] rounded-lg p-4 border border-[#21262d]">
          <h3 className="text-lg font-semibold text-white mb-3">Email Details</h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-400">Subject</p>
              <p className="text-white font-medium">{analysis.subject}</p>
            </div>
            {analysis.suspicious_links && analysis.suspicious_links.length > 0 && (
              <div>
                <p className="text-sm text-gray-400 mb-2">Suspicious Links</p>
                <div className="space-y-2">
                  {analysis.suspicious_links.map((link, index) => (
                    <div key={index} className="bg-red-500/10 border border-red-500/30 rounded p-2">
                      <p className="text-red-400 text-sm font-mono break-all">{link.url}</p>
                      <p className="text-red-300 text-xs">Score: {(link.score * 100).toFixed(1)}%</p>
                      {link.reasons.length > 0 && (
                        <p className="text-red-300 text-xs">Reasons: {link.reasons.join(', ')}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Chat-specific content */}
      {isChat && (
        <div className="bg-[#0D1117] rounded-lg p-4 border border-[#21262d]">
          <h3 className="text-lg font-semibold text-white mb-3">Chat Messages</h3>
          <div className="space-y-2">
            {analysis.messages.map((message, index) => (
              <div key={index} className="bg-[#161b22] rounded p-3">
                <p className="text-gray-300 text-sm">{message}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )



  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-[#010409] border border-[#21262d] rounded-lg w-full max-w-4xl h-[80vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-[#21262d]">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
              analysis.risk_level === 'HIGH' ? 'bg-red-500/20' :
              analysis.risk_level === 'MEDIUM' ? 'bg-yellow-500/20' :
              'bg-green-500/20'
            }`}>
              {getRiskIcon(analysis.risk_level)}
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">
                {messageType.toUpperCase()} Analysis Results
              </h3>
              <p className="text-sm text-gray-400">
                Analysis ID: {analysis.analysis_id}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors p-2 hover:bg-[#21262d] rounded-lg"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>


        {/* Content */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4 scrollbar-thin scrollbar-thumb-transparent scrollbar-track-transparent" style={{ scrollbarWidth: 'thin', scrollbarColor: 'transparent transparent' }}>
          {renderOverview()}
        </div>
      </div>
    </div>
  )
}
