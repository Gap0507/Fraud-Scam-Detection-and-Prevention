// TypeScript interfaces matching Python FastAPI responses

export interface HighlightedToken {
  text: string
  start: number
  end: number
  category: string
  risk_level: string
}

export interface SuspiciousLink {
  url: string
  score: number
  reasons: string[]
}

export interface DetailedAnalysis {
  phishing_classification?: {
    predicted_label: string
    confidence: number
    is_phishing: boolean
  }
  pattern_analysis?: {
    pattern_scores: Record<string, number>
    found_patterns: Record<string, string[]>
    total_pattern_score: number
    high_risk_categories: string[]
  }
  statistical_analysis?: {
    length: number
    word_count: number
    uppercase_ratio: number
    digit_ratio: number
    special_char_ratio: number
    exclamation_count: number
    question_count: number
    link_count: number
    excessive_caps: boolean
    excessive_digits: boolean
    excessive_special: boolean
    excessive_exclamations: boolean
    excessive_links: boolean
    very_short: boolean
    very_long: boolean
    statistical_score: number
  }
  sender_analysis?: {
    score: number
    reputation: string
    reasons: string[]
  }
  link_analysis?: {
    score: number
    suspicious_links: SuspiciousLink[]
    reasons: string[]
  }
  conversation_analysis?: {
    score: number
    characteristics: {
      total_messages: number
      avg_message_length: number
      total_length: number
      short_messages: number
      long_messages: number
      rapid_messaging: number
      repetition_ratio: number
    }
  }
  sentiment_analysis?: {
    score: number
    sentiment: string
    reasons: string[]
    positive_ratio: number
    negative_ratio: number
    neutral_ratio: number
  }
}

export interface AnalysisResponse {
  analysis_id: string
  channel: string
  risk_score: number
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH'
  is_fraud: boolean
  triggers: string[]
  explanation: string
  highlighted_tokens: HighlightedToken[]
  confidence: number
  processing_time: number
  timestamp: string
  detailed_analysis?: DetailedAnalysis
}

export interface EmailAnalysisResponse extends AnalysisResponse {
  subject: string
  body: string
  suspicious_links: SuspiciousLink[]
}

export interface ChatAnalysisResponse extends AnalysisResponse {
  messages: string[]
}

export interface AnalysisRequest {
  content: string
  channel: 'sms' | 'email' | 'chat'
  sender_info?: string
}

export interface EmailAnalysisRequest {
  subject: string
  body: string
  sender_email?: string
}

export interface ChatAnalysisRequest {
  content: string
  sender_info?: string
}

export interface Message {
  id: string
  sender: string
  preview: string
  riskScore: 'LOW' | 'MEDIUM' | 'HIGH'
  timestamp: string
  content: string
  suspiciousKeywords: string[]
  type: 'sms' | 'chat' | 'email'
  analysis?: AnalysisResponse | EmailAnalysisResponse | ChatAnalysisResponse
  isAnalyzed?: boolean
}

export interface ApiError extends Error {
  status: number
  details?: string
}
