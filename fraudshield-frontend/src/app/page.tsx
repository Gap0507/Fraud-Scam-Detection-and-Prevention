'use client'

import { useState } from 'react'
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const router = useRouter()
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    twoFactor: false
  })
  {/*Hello */}

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    // Demo login - accept any email/password or use demo credentials
    const demoCredentials = {
      email: 'demo@fraudshield.io',
      password: 'demo123'
    }
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Check if it's demo credentials or any valid email format
    if (
      (formData.email === demoCredentials.email && formData.password === demoCredentials.password) ||
      (formData.email.includes('@') && formData.password.length >= 3)
    ) {
      // Store demo user data
      localStorage.setItem('fraudshield_user', JSON.stringify({
        name: 'Alex Johnson',
        email: formData.email || demoCredentials.email,
        avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDcrAPji4y42QOFCupXBJ82tCXar-IsQICxYnYsOkkh5_Mvn0GnJuBMKUKcX06Gsg7Ba-TisFk9xxq2g1Ekhl7E6JGq_-I-BbRSRtfd2loWJDW3OO3IFUIyC73g5g2eJNLORP9PZas56jS-X7C0PhO288XMf0KoFme1giCFae3CS2-0XlfRQZTJEtu3cgCP_kKKejcGmxJ_sccJxgyao72B298OumkSHBKGInJjDWkme1PkzcrSPW9wubIXGqjOsT3Jut2Dfov-8-ek',
        isAuthenticated: true
      }))
      
      // Redirect to dashboard
      router.push('/dashboard')
    } else {
      alert('Invalid credentials. Use any email and password (min 3 chars) or demo@fraudshield.io / demo123')
    }
    
    setIsLoading(false)
  }

  return (
    <div className="flex items-center justify-center min-h-screen relative overflow-hidden bg-[#10111A]">
      {/* Background Gradients */}
      <div className="absolute top-[-20%] left-[-20%] w-[500px] h-[500px] bg-[var(--brand-indigo)] rounded-full filter blur-[150px] opacity-30"></div>
      <div className="absolute bottom-[-20%] right-[-20%] w-[500px] h-[500px] bg-[var(--accent-teal)] rounded-full filter blur-[150px] opacity-20"></div>
      
      {/* Main Login Card */}
      <main className="w-full max-w-md p-8 space-y-8 rounded-2xl z-10 glass-morphism shadow-2xl shadow-black/20">
        {/* Header */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="relative">
              <svg 
                className="h-16 w-16 text-[var(--accent-teal)]" 
                fill="currentColor" 
                height="24" 
                viewBox="0 0 24 24" 
                width="24" 
                xmlns="http://www.w3.org/2000/svg"
              >
                <path d="M12 2L2 7V13.53C2 18.23 6.13 22.45 12 23.8C17.87 22.45 22 18.23 22 13.53V7L12 2ZM12 4.14L19.98 8.24V13.53C19.98 17.14 16.54 20.31 12 21.65C7.46 20.31 4.02 17.14 4.02 13.53V8.24L12 4.14Z"></path>
                <path d="M11 15.5V17H13V15.5C14.1 15.22 15 14.23 15 13C15 11.62 13.88 10.5 12.5 10.5C11.12 10.5 10 11.62 10 13C10 14.23 10.9 15.22 11 15.5ZM12.5 8.5C13.88 8.5 15 9.62 15 11H13.5C13.5 10.45 13.05 10 12.5 10C11.95 10 11.5 10.45 11.5 11H10C10 9.62 11.12 8.5 12.5 8.5Z" fill="rgba(255,255,255,0.2)"></path>
              </svg>
              <span 
                className="material-symbols-outlined absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-2xl text-white opacity-80" 
                style={{fontVariationSettings: "'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 48"}}
              >
                assured_workload
              </span>
            </div>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Welcome to FraudShield</h1>
          <p className="text-gray-400 mt-2">Sign in to protect your assets</p>
        </div>

        {/* Login Form */}
        <form className="space-y-6" onSubmit={handleSubmit}>
          {/* Email Field */}
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">mail</span>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="Email address"
              required
              autoComplete="email"
              className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[var(--accent-teal)] focus:border-[var(--accent-teal)] transition-all duration-300 text-white"
            />
          </div>

          {/* Password Field */}
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">lock</span>
            <input
              type={showPassword ? 'text' : 'password'}
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="Password"
              required
              autoComplete="current-password"
              className="w-full pl-10 pr-12 py-3 bg-white/5 border border-white/10 rounded-lg placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[var(--accent-teal)] focus:border-[var(--accent-teal)] transition-all duration-300 text-white"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
            >
              {showPassword ? (
                <EyeSlashIcon className="h-5 w-5" />
              ) : (
                <EyeIcon className="h-5 w-5" />
              )}
            </button>
          </div>

          {/* 2FA and Forgot Password */}
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="two-factor"
                name="twoFactor"
                checked={formData.twoFactor}
                onChange={handleInputChange}
                className="h-4 w-4 rounded border-gray-300/30 text-[var(--accent-teal)] focus:ring-[var(--accent-teal)] bg-transparent"
              />
              <label htmlFor="two-factor" className="ml-2 block text-sm text-gray-300">
                Enable 2FA
              </label>
            </div>
            <div className="text-sm">
              <a 
                href="#" 
                className="font-medium text-[var(--accent-teal)] hover:text-[var(--accent-teal)]/80 transition-colors"
              >
                Forgot your password?
              </a>
            </div>
          </div>

          {/* Login Button */}
          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-gray-900 bg-[var(--accent-teal)] hover:bg-[var(--accent-teal)]/80 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-[var(--accent-teal)] transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {isLoading ? 'Signing In...' : 'Log In'}
            </button>
          </div>
        </form>

        {/* Social Login Divider */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-white/10"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="bg-[#10111A] px-2 text-gray-400 glass-morphism rounded-full">Or continue with</span>
          </div>
        </div>

        {/* Social Login Buttons */}
        <div>
          <div className="grid grid-cols-2 gap-4">
            <button className="w-full inline-flex justify-center py-3 px-4 border border-white/10 rounded-lg shadow-sm bg-white/5 hover:bg-white/10 text-sm font-medium text-white transition-colors duration-300">
              <img 
                alt="Google" 
                className="w-5 h-5 mr-2" 
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuD8_ylhzUQP4TvvvDloCGCIVSBY5nkFAvJE_lD_EIFu1C7IaOg6QitVotkQ2W8NzvWe8XC9eOj7dWmqfe6Yl-LpQx1u3B1cye7gDAV9sDTz7gbm8jsO5pKMY4N1tiRKafcPVJiSXHJ9TC-ruRwEhTM5OgqmFF0oOZSoSbLWXQDwQvJ0PyDSUqdEhXl0-loSCtV9p7lC_N5q1ZQWvOZntlPhZiTwlwok2_IrJBzHRO64kP3eOXF70e5SjG-GmUqwPwDEEsEo6YO_m7kr"
              />
              Google
            </button>
            <button className="w-full inline-flex justify-center py-3 px-4 border border-white/10 rounded-lg shadow-sm bg-white/5 hover:bg-white/10 text-sm font-medium text-white transition-colors duration-300">
              <img 
                alt="Apple" 
                className="w-5 h-5 mr-2" 
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuDAVflm-TuJ8U-ErHcAP5kq1swO7Q1i3PbmpahPpp0Gm4CBMNAIQbka0mRdeqWT7rID2-FXLlaWNKXP9QzXiJDDx2LvaQ8O4miMA23dTqqAxbbQ84gq2TqYzfndh-ctaXToDDg0Z_OrtNUgnjHh2u8shEd73oizqZTLMbEnzCdZKN1hU8g05c0tpFgliikahYF2iddZ26G1EMNoQWh7DColjJlm12L-AiGPuOoDVq5pRJoooPnOVl5N1L9ijN6da5m55edfjY6ZFpJC" 
                style={{filter: 'invert(1)'}}
              />
              Apple
            </button>
          </div>
        </div>

        {/* Sign Up Link */}
        <p className="text-center text-sm text-gray-400">
          Don't have an account?{' '}
          <a 
            href="#" 
            className="font-medium text-[var(--accent-teal)] hover:text-[var(--accent-teal)]/80 transition-colors"
          >
            Sign up
          </a>
        </p>
      </main>
    </div>
  )
}