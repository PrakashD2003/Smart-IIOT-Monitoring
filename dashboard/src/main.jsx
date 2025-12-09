import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';      // ← must be present
import App from './App';

createRoot(document.getElementById('root')).render(<App />);
