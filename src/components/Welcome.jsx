import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import BlobButton from './BlobButton';

const Welcome = () => {
  const [animate, setAnimate] = useState(false);
  const [currentSlide, setCurrentSlide] = useState(0);
  const navigate = useNavigate();
  const location = useLocation();
  const userName = location.state?.name || 'User';

  useEffect(() => {
    // If no name is provided, redirect to login
    if (!location.state?.name) {
      navigate('/login');
      return;
    }
    setAnimate(true);
  }, [location.state, navigate]);

  const slides = [
    {
      title: `Welcome to skill3, ${userName}!`,
      description: "Let us decode your resume into actionable skills and guide you to your dream role.",
      buttonText: "Continue"
    },
    {
      title: "Let's start by learning more about you!",
      description: "Be yourself and answer the questions honestly to help us come up with the best career path for you.",
      buttonText: "Next"
    },
    // Add more slides as needed
  ];

  const handleContinue = () => {
    if (currentSlide < slides.length - 1) {
      setCurrentSlide(prev => prev + 1);
    } else {
      navigate('/study'); // Navigate to StudyPage
    }
  };

  return (
    <div className="flex flex-col md:flex-row fixed inset-0 bg-[#0A0A0F]">
      {/* Left section with illustration */}
      <div className={`absolute md:relative top-0 w-full md:w-1/2 h-[20vh] md:h-[90vh] transition-opacity duration-1000 ${animate ? 'opacity-100' : 'opacity-0'}`}>
        <img
          src="/softskills.jpeg"
          alt="Soft Skills Illustration"
          className="w-full h-full object-cover"
        />
      </div>

      {/* Right section with welcome message */}
      <div className="w-full md:w-1/2 flex items-center justify-center p-12 relative overflow-hidden mt-[20vh] md:mt-0">
        {/* Decorative background circles */}
        <svg
          className="absolute inset-0 w-full h-full"
          viewBox="0 0 100 100"
          preserveAspectRatio="xMidYMid slice"
        >
          <defs>
            <radialGradient id="circleGradient" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#1F2937" /> {/* gray-800 */}
              <stop offset="100%" stopColor="#111827" /> {/* gray-900 */}
            </radialGradient>
          </defs>
          <circle
            cx="80"
            cy="20"
            r="60"
            fill="url(#circleGradient)"
            opacity="0.8"
          />
          <circle
            cx="20"
            cy="80"
            r="40"
            fill="url(#circleGradient)"
            opacity="0.6"
          />
          <circle
            cx="65"
            cy="70"
            r="35"
            fill="url(#circleGradient)"
            opacity="0.4"
          />
        </svg>

        {/* Content container */}
        <div className="w-full max-w-md space-y-12 relative z-10">
          <div className={`animate-fade-in-down opacity-0 ${animate ? 'opacity-100' : ''}`}>
            <div className="text-center space-y-4">
              <h2 className="text-3xl font-bold text-white">{slides[currentSlide].title}</h2>
              <p className="text-gray-400">{slides[currentSlide].description}</p>
              {slides[currentSlide].content}
            </div>
          </div>

          {/* Progress dots */}
          <div className="flex justify-center space-x-4 mb-12">
            {slides.map((_, index) => (
              <div
                key={index}
                className={`h-3 w-3 rounded-full transition-all duration-300 ${
                  index === currentSlide ? 'bg-blue-500 w-6' : 'bg-gray-600'
                }`}
              />
            ))}
          </div>

          <div className={`animate-fade-in-up opacity-0 ${animate ? 'opacity-100' : ''} pt-8`}>
            <BlobButton
              onClick={handleContinue}
              className="w-full text-lg py-4"
            >
              {slides[currentSlide].buttonText}
            </BlobButton>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Welcome;
