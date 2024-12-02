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
    navigate('/next-step');
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
      <div className="flex-grow px-4 py-6 md:px-6 md:py-10 flex flex-col items-center">
        <h1 className="text-xl md:text-2xl font-semibold mb-8 md:mb-16 text-center">
          What's your preferred career path?
        </h1>

        <div className="flex flex-col md:flex-row justify-around w-full max-w-full md:max-w-4xl mb-8 md:mb-16 space-y-4 md:space-y-0 md:space-x-6">
          <button
            onClick={() => handleSelect('Specialist')}
            className={`flex-1 border border-gray-500 px-6 py-2 rounded-lg hover:bg-gray-800 transition-colors ${selectedPath === 'Specialist' ? 'bg-gray-700' : ''}`}
          >
            Specialist
          </button>

          <button
            onClick={() => handleSelect('Leadership')}
            className={`flex-1 border border-gray-500 px-6 py-2 rounded-lg hover:bg-gray-800 transition-colors ${selectedPath === 'Leadership' ? 'bg-gray-700' : ''}`}
          >
            Leadership
          </button>

          <button
            onClick={() => handleSelect("I don't have a preferred career path")}
            className={`flex-1 border border-gray-500 px-6 py-2 rounded-lg hover:bg-gray-800 transition-colors ${selectedPath === "I don't have a preferred career path" ? 'bg-gray-700' : ''}`}
          >
            I don't have a preferred career path
          </button>
        </div>

        <div className="flex flex-col md:flex-row justify-around w-full max-w-full md:max-w-2xl space-y-4 md:space-y-0 md:space-x-6">
          <button className="flex-1 bg-transparent text-white hover:bg-gray-800 px-4 py-3 rounded-lg">
            Skip for now
          </button>

          <BlobButton
            onClick={handleContinue}
            className="flex-1 bg-blue-500 text-white"
          >
            Continue
          </BlobButton>
        </div>
      </div>
    </div>
  );
};

export default CareerPathPage;