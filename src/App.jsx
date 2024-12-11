import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import SignIn from './components/SignIn'
import Login from './components/Login'
import Welcome from './components/Welcome';
import StudyPage from './components/StudyPage';
import ManualUniversityPage from './components/ManualUniversityPage';
import CareerPathPage from './components/CareerPathPage';
import PersonalityPage from './components/PersonalityPage';
import PersonalityQuiz from './components/PersonalityQuiz';
import WorkModelPage from './components/WorkModelPage';
import CareerGoalPage from './components/CareerGoalPage';
import IndustryPage from './components/IndustryPage';
import CompanyPage from './components/CompanyPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignIn />} />
        <Route path="/welcome" element={<Welcome />} />
        <Route path="/study" element={<StudyPage />} />
        <Route path="/manual-university" element={<ManualUniversityPage />} />
        <Route path="/career-path" element={<CareerPathPage />} />
        <Route path="/personality" element={<PersonalityPage />} />
        <Route path="/personality-quiz" element={<PersonalityQuiz />} />
        <Route path="/work-model" element={<WorkModelPage />} />
        <Route path="/career-goal" element={<CareerGoalPage />} />
        <Route path="/industry" element={<IndustryPage />} />
        <Route path="/company" element={<CompanyPage />} />
      </Routes>
    </Router>
  );
}

export default App
