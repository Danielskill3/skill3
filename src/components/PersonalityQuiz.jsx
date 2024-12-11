import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import BlobButton from './BlobButton';
import { FaArrowLeft } from 'react-icons/fa';

const PersonalityQuiz = () => {
  const navigate = useNavigate();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const questions = [
    {
      id: 1,
      text: "How do you prefer to spend your free time?",
      options: [
        { text: "Reading or learning something new", value: "I" },
        { text: "Socializing with friends", value: "E" },
        { text: "Working on personal projects", value: "J" },
        { text: "Going with the flow, being spontaneous", value: "P" }
      ]
    },
    {
      id: 2,
      text: "When making decisions, you typically:",
      options: [
        { text: "Follow your heart and consider others' feelings", value: "F" },
        { text: "Analyze facts and use logic", value: "T" },
        { text: "Consider both but lean towards practical outcomes", value: "S" },
        { text: "Look for creative possibilities", value: "N" }
      ]
    },
    {
      id: 3,
      text: "In group situations, you tend to:",
      options: [
        { text: "Take charge and organize others", value: "E" },
        { text: "Observe and contribute when needed", value: "I" },
        { text: "Support others' ideas", value: "F" },
        { text: "Analyze and improve plans", value: "T" }
      ]
    },
    {
      id: 4,
      text: "When approaching a new project, you prefer to:",
      options: [
        { text: "Plan everything in detail", value: "J" },
        { text: "Start immediately and adjust as needed", value: "P" },
        { text: "Research thoroughly first", value: "N" },
        { text: "Follow proven methods", value: "S" }
      ]
    },
    {
      id: 5,
      text: "When dealing with problems, you typically:",
      options: [
        { text: "Trust your instincts and feelings", value: "F" },
        { text: "Analyze patterns and facts", value: "T" },
        { text: "Look for practical solutions", value: "S" },
        { text: "Consider multiple possibilities", value: "N" }
      ]
    },
    {
      id: 6,
      text: "How do you approach challenges?",
      options: [
        { text: "Head-on, I love a good challenge!", value: "E" },
        { text: "I prefer to think it through first.", value: "I" },
        { text: "I analyze all possible outcomes.", value: "T" },
        { text: "I seek advice from friends.", value: "F" }
      ]
    },
    {
      id: 7,
      text: "What motivates you?",
      options: [
        { text: "Achieving my goals.", value: "J" },
        { text: "Learning new things.", value: "N" },
        { text: "Helping others.", value: "F" },
        { text: "Having fun and enjoying life.", value: "P" }
      ]
    },
    {
      id: 8,
      text: "How do you prefer to communicate?",
      options: [
        { text: "In person, I love face-to-face conversations!", value: "E" },
        { text: "Through texts or emails, it’s more convenient.", value: "I" },
        { text: "I prefer to write things down.", value: "J" },
        { text: "I like to keep it casual and spontaneous.", value: "P" }
      ]
    },
    {
      id: 9,
      text: "When it comes to planning, you:",
      options: [
        { text: "Always have a detailed plan.", value: "J" },
        { text: "Have a rough idea but stay flexible.", value: "P" },
        { text: "Prefer to go with the flow.", value: "N" },
        { text: "Like to involve others in the planning.", value: "E" }
      ]
    },
    {
      id: 10,
      text: "In social situations, you tend to:",
      options: [
        { text: "Be the life of the party!", value: "E" },
        { text: "Enjoy one-on-one conversations.", value: "I" },
        { text: "Observe and listen more than talk.", value: "N" },
        { text: "Make sure everyone feels included.", value: "F" }
      ]
    }
  ];

  const handleAnswer = (value) => {
    setAnswers(prev => ({
      ...prev,
      [currentQuestion]: value
    }));

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    } else {
      analyzePersonality();
    }
  };

  const analyzePersonality = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${import.meta.env.NODE_ENV === 'production' ? 'https://skill3.onrender.com/api/analyze-personality' : 'http://localhost:8000/api/analyze-personality'}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ answers }),
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data.personality);
      } else {
        console.error('Failed to analyze personality');
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleContinue = () => {
    navigate('/personality', { state: { personality: result } });
  };

  return (
    <div className="fixed inset-0 bg-[#0A0A0F] text-white flex flex-col">
      {/* Top section with progress bar */}
      <div className="px-6 py-4">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="text-white p-2">
            <FaArrowLeft />
          </button>
          <div className="w-full bg-[#1A1A1F] h-2 rounded-full">
            <div 
              className="bg-blue-500 h-full rounded-full transition-all duration-300" 
              style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-grow px-6 py-8 overflow-y-auto pb-24">
        {!result ? (
          <>
            <div className="flex items-center gap-4 mb-8">
              <div className="w-8 h-8 bg-[#1A1A1F] rounded-lg flex items-center justify-center">
                🤔
              </div>
              <h1 className="text-2xl font-medium">
                {questions[currentQuestion].text}
              </h1>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {questions[currentQuestion].options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => handleAnswer(option.value)}
                  className="py-4 px-6 bg-transparent border border-[#2A2A2F] rounded-lg hover:border-gray-600 transition-all duration-300 text-left text-lg hover:scale-102 hover:shadow-lg"
                >
                  {option.text}
                </button>
              ))}
            </div>
          </>
        ) : (
          <div className="text-center space-y-8">
            <div className="text-6xl mb-4">🎉</div>
            <h2 className="text-3xl font-bold">Your Personality Type</h2>
            <div className="text-5xl font-bold text-blue-500">{result}</div>
            <p className="text-gray-400 max-w-md mx-auto">
              Based on your answers, you align most with the {result} personality type.
            </p>
            <BlobButton
              onClick={handleContinue}
              className="mt-8"
            >
              Continue with this result
            </BlobButton>
          </div>
        )}
      </div>

      {isLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      )}
    </div>
  );
};

export default PersonalityQuiz;
