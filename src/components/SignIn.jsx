import { useState, useEffect } from 'react';
import { FaLinkedin, FaEye, FaEyeSlash } from 'react-icons/fa';
import jobSearchIllustration from '../assets/job-search-illustration.svg';
import { Link, useNavigate } from 'react-router-dom';
import BlobButton from './BlobButton';

export default function SignIn() {
  const navigate = useNavigate();
  const [animate, setAnimate] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  useEffect(() => {
    setAnimate(true);
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords don't match");
      return;
    }
    
    setIsLoading(true);
    try {
      const response = await fetch('https://skill3.onrender.com/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          password: formData.password
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        navigate('/login', { 
          state: { 
            message: 'Registration successful! Please login with your credentials.',
            email: formData.email
          }
        });
      } else {
        setError(data.error || 'Registration failed');
      }
    } catch (err) {
      setError('Failed to connect to server');
    } finally {
      setIsLoading(false);
    }
  };

  const checkPasswordStrength = (password) => {
    let strength = 0;
    if (password.length >= 8) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;
    return strength;
  };

  const getPasswordStrengthColor = () => {
    switch (checkPasswordStrength(formData.password)) {
      case 0: return 'bg-red-500';
      case 1: return 'bg-orange-500';
      case 2: return 'bg-yellow-500';
      case 3: return 'bg-blue-500';
      case 4: return 'bg-green-500';
      default: return 'bg-gray-300';
    }
  };

  const getPasswordStrengthText = () => {
    switch (checkPasswordStrength(formData.password)) {
      case 0: return 'Very Weak';
      case 1: return 'Weak';
      case 2: return 'Fair';
      case 3: return 'Good';
      case 4: return 'Strong';
      default: return '';
    }
  };

  return (
    <div className="flex flex-col md:flex-row fixed inset-0 bg-[#0A0A0F]">
      {/* Image section - will appear on top for mobile */}
      <div className={`absolute md:relative top-0 w-full md:w-1/2 h-[20vh] md:h-screen transition-opacity duration-1000 ${animate ? 'opacity-100' : 'opacity-0'}`}>
        <img
          src="/jobs.jpeg"
          alt="Job Search"
          className="w-full h-full object-cover"
        />
      </div>

      {/* Form section */}
      <div className="w-full md:w-1/2 min-h-[80vh] md:min-h-screen flex items-center justify-center px-8 py-6 md:py-0 overflow-y-auto mt-[20vh] md:mt-0">
        <div className="w-full max-w-md space-y-10">
          <div className={`animate-fade-in-down opacity-0 ${animate ? 'opacity-100' : ''}`}>
            <h1 className="text-5xl font-bold text-white text-center mb-10">
              Let's Get Started
            </h1>
            {error && (
              <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                {error}
              </div>
            )}
          </div>

          <form onSubmit={handleSubmit} className="mt-8 space-y-8">
            <div className="space-y-8">
              <div className={`animate-fade-in-down opacity-0 ${animate ? 'opacity-100' : ''}`} style={{ animationDelay: '200ms' }}>
                <div className="relative">
                  <input
                    type="email"
                    name="email"
                    id="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    placeholder="Email Address"
                    className="peer w-full px-6 py-4 text-lg rounded-lg bg-[#1A1A1F] border border-gray-800 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all focus:placeholder-transparent"
                  />
                  <label
                    htmlFor="email"
                    className="absolute -top-6 left-0 text-sm text-gray-400 opacity-0 transition-all duration-300 peer-focus:opacity-100 peer-focus:text-blue-500"
                  >
                    Email Address
                  </label>
                </div>
              </div>

              <div className={`animate-fade-in-down opacity-0 ${animate ? 'opacity-100' : ''}`} style={{ animationDelay: '400ms' }}>
                <div className="relative">
                  <input
                    type="text"
                    name="name"
                    id="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    placeholder="Full Name"
                    className="peer w-full px-6 py-4 text-lg rounded-lg bg-[#1A1A1F] border border-gray-800 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all focus:placeholder-transparent"
                  />
                  <label
                    htmlFor="name"
                    className="absolute -top-6 left-0 text-sm text-gray-400 opacity-0 transition-all duration-300 peer-focus:opacity-100 peer-focus:text-blue-500"
                  >
                    Full Name
                  </label>
                </div>
              </div>

              <div className={`space-y-2 animate-fade-in-down opacity-0 ${animate ? 'opacity-100' : ''}`} style={{ animationDelay: '600ms' }}>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    id="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    placeholder="Password"
                    className="peer w-full px-6 py-4 text-lg rounded-lg bg-[#1A1A1F] border border-gray-800 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all focus:placeholder-transparent"
                  />
                  <label
                    htmlFor="password"
                    className="absolute -top-6 left-0 text-sm text-gray-400 opacity-0 transition-all duration-300 peer-focus:opacity-100 peer-focus:text-blue-500"
                  >
                    Password
                  </label>
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-300 focus:outline-none"
                  >
                    {showPassword ? <FaEyeSlash size={20} /> : <FaEye size={20} />}
                  </button>
                  {formData.password && (
                    <div className="space-y-1 mt-2">
                      <div className="flex gap-1 h-1">
                        {[...Array(4)].map((_, i) => (
                          <div
                            key={i}
                            className={`h-full w-1/4 rounded-full transition-colors duration-300 ${
                              i < checkPasswordStrength(formData.password) ? getPasswordStrengthColor() : 'bg-gray-700'
                            }`}
                          />
                        ))}
                      </div>
                      <p className={`text-sm ${getPasswordStrengthColor().replace('bg-', 'text-')} transition-colors`}>
                        {getPasswordStrengthText()}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              <div className={`space-y-2 animate-fade-in-down opacity-0 ${animate ? 'opacity-100' : ''}`} style={{ animationDelay: '800ms' }}>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="confirmPassword"
                    id="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    required
                    placeholder="Confirm Password"
                    className="peer w-full px-6 py-4 text-lg rounded-lg bg-[#1A1A1F] border border-gray-800 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all focus:placeholder-transparent"
                  />
                  <label
                    htmlFor="confirmPassword"
                    className="absolute -top-6 left-0 text-sm text-gray-400 opacity-0 transition-all duration-300 peer-focus:opacity-100 peer-focus:text-blue-500"
                  >
                    Confirm Password
                  </label>
                </div>
              </div>
            </div>

            <div className={`animate-fade-in-up opacity-0 mt-10 ${animate ? 'opacity-100' : ''}`} style={{ animationDelay: '1000ms' }}>
              <BlobButton
                type="submit"
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? 'Creating Account...' : 'Create Account'}
              </BlobButton>
            </div>

            <div className={`relative animate-fade-in-up opacity-0 ${animate ? 'opacity-100' : ''}`} style={{ animationDelay: '1200ms' }}>
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-800"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-[#0A0A0F] text-gray-400">OR</span>
              </div>
            </div>

            <div className={`animate-fade-in-up opacity-0 ${animate ? 'opacity-100' : ''}`} style={{ animationDelay: '1400ms' }}>
              <button
                type="button"
                className="w-full px-6 py-4 text-lg font-semibold text-blue-600 bg-[#1A1A1F] border border-gray-800 rounded-lg hover:bg-[#222228] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900 transition-colors flex items-center justify-center gap-3"
              >
                <FaLinkedin className="text-[#0A66C2]" size={20} />
                Continue with LinkedIn
              </button>
            </div>

            <p className="text-center text-gray-400 text-lg mt-8">
              Already have an account?{' '}
              <Link to="/login" className="text-blue-500 hover:text-blue-400 font-semibold">
                Log in
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};
