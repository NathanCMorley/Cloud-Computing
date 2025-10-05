import './styles/App.css'
import NavBar from './components/NavBar.jsx'
import Home from './pages/Home.jsx'
import Map from './pages/Map.jsx'
import About from './pages/About.jsx'
import { Routes, Route } from 'react-router-dom'
import './styles/index.css'

function App() {
  return (
    <>
      <NavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/home" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/map" element={<Map />} />
      </Routes>
    </>
  );
}

export default App
