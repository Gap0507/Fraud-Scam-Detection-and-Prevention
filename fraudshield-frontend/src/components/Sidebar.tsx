'use client'

import { useState, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { 
  HomeIcon, 
  ChatBubbleLeftRightIcon, 
  PhoneIcon, 
  DocumentTextIcon, 
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline'

interface User {
  name: string
  email: string
  avatar: string
  isAuthenticated: boolean
}

export default function Sidebar() {
  const router = useRouter()
  const pathname = usePathname()
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    // Check if user is authenticated
    const userData = localStorage.getItem('fraudshield_user')
    if (userData) {
      setUser(JSON.parse(userData))
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('fraudshield_user')
    router.push('/')
  }

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: HomeIcon, href: '/dashboard' },
    { id: 'text-channels', label: 'Text Channels', icon: ChatBubbleLeftRightIcon, href: '/text-channels' },
    { id: 'voice-channels', label: 'Voice Channels', icon: PhoneIcon, href: '/voice-channels' },
    { id: 'transaction-channels', label: 'Transaction Channels', icon: DocumentTextIcon, href: '/transaction-channels' },
    { id: 'settings', label: 'Settings', icon: Cog6ToothIcon, href: '/settings' }
  ]

  // Don't show sidebar on login page
  if (pathname === '/') {
    return null
  }

  return (
    <div className="w-64 bg-[#010409] border-r border-[#21262d] flex flex-col h-screen">
      {/* Logo */}
      <div className="flex items-center gap-2 px-4 py-6 border-b border-[#21262d]">
        <div className="w-8 h-8 bg-[var(--accent-teal)] rounded-lg flex items-center justify-center">
          <span className="material-symbols-outlined text-white text-lg">shield</span>
        </div>
        <h1 className="text-xl font-bold">FraudShield</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4">
        <div className="space-y-2">
          {navigationItems.map((item) => (
            <button
              key={item.id}
              onClick={() => router.push(item.href)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                pathname === item.href
                  ? 'bg-[#161b22] text-white'
                  : 'text-gray-400 hover:bg-[#161b22] hover:text-white'
              }`}
            >
              <item.icon className="w-5 h-5" />
              {item.label}
            </button>
          ))}
        </div>
      </nav>

      {/* User Profile */}
      {user && (
        <div className="p-4 border-t border-[#21262d]">
          <div className="flex items-center gap-3 p-3 rounded-lg bg-[#161b22]">
            <img
              src={user.avatar}
              alt="User avatar"
              className="w-10 h-10 rounded-full"
            />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-white truncate">{user.name}</p>
              <p className="text-xs text-gray-400 truncate">{user.email}</p>
            </div>
            <button
              onClick={handleLogout}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
