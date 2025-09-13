'use client'

import { useState } from 'react'
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
  const [activeTab, setActiveTab] = useState<'overview' | 'details' | 'tokens'>('overview')

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

  const renderDetails = () => {
    if (!analysis.detailed_analysis) {
      return (
        <div className="text-center py-8">
          <p className="text-gray-400">No detailed analysis available</p>
        </div>
      )
    }

    const details = analysis.detailed_analysis

    return (
      <div className="space-y-6">
        {/* Pattern Analysis */}
        {details.pattern_analysis && (
          <div className="bg-[#0D1117] rounded-lg p-4 border border-[#21262d]">
            <h3 className="text-lg font-semibold text-white mb-3">Pattern Analysis</h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-400">Overall Pattern Score</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-[var(--accent-teal)] h-2 rounded-full transition-all duration-300"
                      style={{ width: `${details.pattern_analysis.total_pattern_score * 100}%` }}
                    />
                  </div>
                  <span className="text-white text-sm font-medium">
                    {(details.pattern_analysis.total_pattern_score * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
              {details.pattern_analysis.high_risk_categories.length > 0 && (
                <div>
                  <p className="text-sm text-gray-400 mb-2">High-Risk Categories</p>
                  <div className="flex flex-wrap gap-2">
                    {details.pattern_analysis.high_risk_categories.map((category, index) => (
                      <span
                        key={index}
                        className="bg-red-500/20 text-red-400 text-xs px-2 py-1 rounded border border-red-500/30"
                      >
                        {category.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Statistical Analysis */}
        {details.statistical_analysis && (
          <div className="bg-[#0D1117] rounded-lg p-4 border border-[#21262d]">
            <h3 className="text-lg font-semibold text-white mb-3">Statistical Analysis</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-400">Length</p>
                <p className="text-white font-medium">{details.statistical_analysis.length} chars</p>
              </div>
              <div>
                <p className="text-gray-400">Word Count</p>
                <p className="text-white font-medium">{details.statistical_analysis.word_count}</p>
              </div>
              <div>
                <p className="text-gray-400">Uppercase Ratio</p>
                <p className="text-white font-medium">{(details.statistical_analysis.uppercase_ratio * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-gray-400">Special Chars</p>
                <p className="text-white font-medium">{(details.statistical_analysis.special_char_ratio * 100).toFixed(1)}%</p>
              </div>
            </div>
          </div>
        )}

        {/* Sender Analysis */}
        {details.sender_analysis && (
          <div className="bg-[#0D1117] rounded-lg p-4 border border-[#21262d]">
            <h3 className="text-lg font-semibold text-white mb-3">Sender Analysis</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-400">Reputation</span>
                <span className={`font-medium ${
                  details.sender_analysis.reputation === 'suspicious' ? 'text-red-400' :
                  details.sender_analysis.reputation === 'legitimate' ? 'text-green-400' :
                  'text-yellow-400'
                }`}>
                  {details.sender_analysis.reputation}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Score</span>
                <span className="text-white font-medium">{(details.sender_analysis.score * 100).toFixed(1)}%</span>
              </div>
              {details.sender_analysis.reasons.length > 0 && (
                <div>
                  <p className="text-gray-400 text-sm mb-1">Reasons</p>
                  <ul className="text-sm text-gray-300 space-y-1">
                    {details.sender_analysis.reasons.map((reason, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="text-gray-500">•</span>
                        <span>{reason}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Sentiment Analysis (for chat) */}
        {details.sentiment_analysis && (
          <div className="bg-[#0D1117] rounded-lg p-4 border border-[#21262d]">
            <h3 className="text-lg font-semibold text-white mb-3">Sentiment Analysis</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Overall Sentiment</span>
                <span className={`font-medium ${
                  details.sentiment_analysis.sentiment === 'positive' ? 'text-green-400' :
                  details.sentiment_analysis.sentiment === 'negative' ? 'text-red-400' :
                  'text-yellow-400'
                }`}>
                  {details.sentiment_analysis.sentiment}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-gray-400">Positive</p>
                  <p className="text-green-400 font-medium">{(details.sentiment_analysis.positive_ratio * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-gray-400">Negative</p>
                  <p className="text-red-400 font-medium">{(details.sentiment_analysis.negative_ratio * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-gray-400">Neutral</p>
                  <p className="text-yellow-400 font-medium">{(details.sentiment_analysis.neutral_ratio * 100).toFixed(1)}%</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }

  const renderTokens = () => (
    <div className="space-y-4">
      {analysis.highlighted_tokens.length > 0 ? (
        <div className="space-y-3">
          {analysis.highlighted_tokens.map((token, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg border ${
                token.risk_level === 'high' 
                  ? 'bg-red-500/10 border-red-500/30' 
                  : 'bg-yellow-500/10 border-yellow-500/30'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-white">{token.text}</span>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-1 rounded ${
                    token.risk_level === 'high' 
                      ? 'bg-red-500/20 text-red-400' 
                      : 'bg-yellow-500/20 text-yellow-400'
                  }`}>
                    {token.risk_level}
                  </span>
                  <span className="text-xs text-gray-400">
                    {token.category.replace('_', ' ')}
                  </span>
                </div>
              </div>
              <p className="text-sm text-gray-400">
                Position: {token.start} - {token.end}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <p className="text-gray-400">No highlighted tokens found</p>
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

        {/* Tab Navigation */}
        <div className="border-b border-[#21262d]">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'details', label: 'Detailed Analysis' },
              { id: 'tokens', label: 'Highlighted Tokens' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-[var(--accent-teal)] text-[var(--accent-teal)]'
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 p-6 overflow-y-auto">
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'details' && renderDetails()}
          {activeTab === 'tokens' && renderTokens()}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-[#21262d] flex gap-3">
          <button className="flex-1 bg-green-600/20 text-green-400 border border-green-600 rounded-md py-2 text-sm font-semibold hover:bg-green-600/30 transition-colors">
            Mark as Safe
          </button>
          <button className="flex-1 bg-red-600/20 text-red-400 border border-red-600 rounded-md py-2 text-sm font-semibold hover:bg-red-600/30 transition-colors">
            Quarantine
          </button>
          <button className="flex-1 bg-blue-600/20 text-blue-400 border border-blue-600 rounded-md py-2 text-sm font-semibold hover:bg-blue-600/30 transition-colors">
            Export Report
          </button>
        </div>
      </div>
    </div>
  )
}
