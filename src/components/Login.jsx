import React, { useState, useEffect } from 'react';
import { FaLinkedin, FaEye, FaEyeSlash } from 'react-icons/fa';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import BlobButton from './BlobButton';

export default function Login() {
  const location = useLocation();
  const navigate = useNavigate();
  const [animate, setAnimate] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: location.state?.email || '',
    password: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(location.state?.message || '');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setAnimate(true);
    // Clear the success message after 5 seconds
    if (success) {
      const timer = setTimeout(() => {
        setSuccess('');
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear any error when user starts typing
    if (error) setError('');
    if (success) setSuccess('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.NODE_ENV === 'production' ? 'https://skill3.onrender.com/login' : 'http://localhost:8000/login'}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      
      if (response.ok) {
        console.log('Login successful, navigating to welcome page');
        console.log('User name:', data.name);
        localStorage.setItem('token', data.token);
        navigate('/welcome', { 
          state: { 
            name: data.name // Pass the name from server response
          }
        });
      } else {
        setError(data.error || 'Login failed');
      }
    } catch (err) {
      setError('Failed to connect to server');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col md:flex-row fixed inset-0 bg-[#0A0A0F]">
      {/* Image section */}
      <div className={`absolute md:relative top-0 w-full md:w-1/2 h-[20vh] md:h-screen transition-opacity duration-1000 ${animate ? 'opacity-100' : 'opacity-0'}`}>
        <img
          src="/login.jpeg"
          alt="Login"
          className="w-full h-full object-cover"
        />
      </div>

      {/* Form section */}
      <div className="w-full md:w-1/2 min-h-[80vh] md:min-h-screen flex items-center justify-center px-8 py-6 md:py-0 overflow-y-auto mt-[20vh] md:mt-0">
        <div className="w-full max-w-md space-y-8">
          <div className={`animate-fade-in-down opacity-0 ${animate ? 'opacity-100' : ''}`}>
            <h1 className="text-4xl md:text-5xl font-bold text-white text-center">Welcome Back</h1>
            <p className="mt-3 text-gray-400 text-center">Please login to continue</p>
          </div>

          {success && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative text-center animate-fade-in">
              {success}
            </div>
          )}

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative text-center animate-fade-in">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-8 space-y-6">
            <div className="space-y-6">
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
                    className="peer w-full px-4 py-3 rounded-lg bg-[#1A1A1F] border border-gray-800 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all focus:placeholder-transparent"
                  />
                  <label
                    htmlFor="email"
                    className="absolute -top-6 left-0 text-sm text-gray-400 opacity-0 transition-all duration-300 peer-focus:opacity-100 peer-focus:text-blue-500"
                  >
                    Email Address
                  </label>
                </div>
              </div>

              <div className={`space-y-2 animate-fade-in-down opacity-0 ${animate ? 'opacity-100' : ''}`} style={{ animationDelay: '400ms' }}>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    id="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    placeholder="Password"
                    className="peer w-full px-4 py-3 rounded-lg bg-[#1A1A1F] border border-gray-800 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all focus:placeholder-transparent"
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
                </div>
              </div>
            </div>

            <div className={`space-y-6 animate-fade-in-down opacity-0 ${animate ? 'opacity-100' : ''}`} style={{ animationDelay: '600ms' }}>
              <BlobButton
                type="submit"
                disabled={isLoading}
              >
                {isLoading ? 'Logging in...' : 'Sign In'}
              </BlobButton>

              <button
                type="button"
                className="w-full px-6 py-4 text-lg font-semibold text-blue-600 bg-[#1A1A1F] border border-gray-800 rounded-lg hover:bg-[#222228] bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900 transition-colors flex items-center justify-center gap-3"
              >
                <FaLinkedin className="text-[#0A66C2]" size={20} />
                Continue with LinkedIn
              </button>
            </div>
          </form>

          <p className="text-center text-gray-400 text-lg mt-8">
            Don't have an account?{' '}
            <Link to="/signup" className="text-blue-500 hover:text-blue-400 font-semibold">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
