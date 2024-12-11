import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaArrowLeft } from 'react-icons/fa';
import BlobButton from './BlobButton';

const CareerPathPage = () => {
  const navigate = useNavigate();
  const [selectedPath, setSelectedPath] = useState(null);

  const handleBack = () => {
    navigate(-1);
  };

  const handleSelect = async (path) => {
    setSelectedPath(path);
    try {
      const response = await fetch(`${import.meta.env.NODE_ENV === 'production' ? 'https://skill3.onrender.com/api/career-path' : 'http://localhost:8000/api/career-path'}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ careerPath: path }),
      });

      if (!response.ok) {
        console.error('Failed to save career path');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleContinue = () => {
    navigate('/personality');
  };

  const handleSkip = () => {
    navigate('/personality');
  };

  return (
    <div className="fixed inset-0 bg-[#0A0A0F] text-white flex flex-col">
      {/* Top section with progress bar */}
      <div className="px-4 py-4 md:px-6 md:py-6">
        <div className="flex items-center gap-4 md:gap-6">
          <button onClick={handleBack} className="text-white p-2">
            <FaArrowLeft />
          </button>
          <div className="w-full bg-[#1A1A1F] h-2 md:h-3 rounded-full">
            <div className="bg-blue-500 h-full rounded-full" style={{ width: '30%' }}></div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-grow px-6 py-8 overflow-y-auto pb-24 flex flex-col">
        <div className="flex items-center gap-4 mb-8">
          <div className="w-8 h-8 bg-[#1A1A1F] rounded-lg flex items-center justify-center">
            🎯
          </div>
          <h1 className="text-xl font-medium">
            What's your preferred career path?
          </h1>
        </div>

        <div className="flex flex-col md:flex-row justify-between w-full gap-4 mb-auto">
          <button
            onClick={() => handleSelect('Specialist')}
            className={`w-full md:w-1/3 py-3 px-4 bg-transparent border border-[#2A2A2F] rounded-lg hover:border-gray-600 transition-all duration-300 text-center ${
              selectedPath === 'Specialist' 
                ? 'bg-[#0066FF] text-white scale-105 shadow-[0_0_30px_rgba(0,102,255,0.3)] border-[#0066FF]' 
                : 'hover:scale-102 hover:shadow-lg'
            }`}
          >
            Specialist
          </button>

          <button
            onClick={() => handleSelect('Leadership')}
            className={`w-full md:w-1/3 py-3 px-4 bg-transparent border border-[#2A2A2F] rounded-lg hover:border-gray-600 transition-all duration-300 text-center ${
              selectedPath === 'Leadership' 
                ? 'bg-[#0066FF] text-white scale-105 shadow-[0_0_30px_rgba(0,102,255,0.3)] border-[#0066FF]' 
                : 'hover:scale-102 hover:shadow-lg'
            }`}
          >
            Leadership
          </button>

          <button
            onClick={() => handleSelect("I don't have a preferred career path")}
            className={`w-full md:w-1/3 py-3 px-4 bg-transparent border border-[#2A2A2F] rounded-lg hover:border-gray-600 transition-all duration-300 text-center ${
              selectedPath === "I don't have a preferred career path" 
                ? 'bg-[#0066FF] text-white scale-105 shadow-[0_0_30px_rgba(0,102,255,0.3)] border-[#0066FF]' 
                : 'hover:scale-102 hover:shadow-lg'
            }`}
          >
            I don't have a preferred career path
          </button>
        </div>
      </div>

      {/* Bottom buttons - fixed at bottom */}
      <div className="fixed bottom-0 left-0 right-0 border-t border-[#2A2A2F] bg-[#0A0A0F]">
        <div className="max-w-full mx-auto px-6 py-4 flex justify-between items-center">
          <button onClick={handleSkip} className="text-gray-400 py-2 hover:text-gray-300 transition-colors">Skip for now</button>
          <BlobButton
            onClick={handleContinue}
            disabled={!selectedPath}
          >
            Continue
          </BlobButton>
        </div>
      </div>
    </div>
  );
};

export default CareerPathPage;