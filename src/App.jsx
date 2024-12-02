import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import SignIn from './components/SignIn'
import Login from './components/Login'
import Welcome from './components/Welcome';
import StudyPage from './components/StudyPage';
import ManualUniversityPage from './components/ManualUniversityPage';
import CareerPathPage from './components/CareerPathPage';

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
      </Routes>
    </Router>
  );
}

export default App
