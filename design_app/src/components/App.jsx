import React from 'react';
import {
  BrowserRouter, Navigate, Routes, Route,
} from 'react-router-dom';

import MainLayout from './MainLayout';
import Home from '../pages/Home';
import Wire from '../pages/Wire';
import WireOld from '../pages/Wire-old';
import Settings from '../pages/Settings';
import Company from '../pages/Company';
import MyTopics from '../pages/MyTopics';
import SaveTopic from '../pages/SaveTopic';
import MyDashboard from '../pages/MyDashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route path="" element={<Home />} />
          <Route path="wire" element={<Wire />} />
          <Route path="wire-old" element={<WireOld />} />
          <Route path="settings" element={<Settings />} />   
          <Route path="company" element={<Company />} />   
          <Route path="mytopics" element={<MyTopics />} />   
          <Route path="savetopic" element={<SaveTopic />} />   
          <Route path="mydashboard" element={<MyDashboard />} />
        </Route>          
      </Routes>      
    </BrowserRouter>
  );
}

export default App;
