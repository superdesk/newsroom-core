import React from 'react';
import { Outlet } from 'react-router-dom';

import MainNavbar from './MainNavbar';
import SideNav from './SideNav';

function MainLayout() {
  return (
        <div className="newsroomWrap">
            <MainNavbar />
            <div className="contentWrap flex-md-p-row flex-lg-l-row">
                <SideNav />
                <Outlet />
            </div>
            <footer className="footer" id="footer">
              <div className="d-none d-md-block me-3">
                  © The Canadian Press 2023
              </div>
              <div>
                  <a href="#" target="_blank">Terms of Use</a>
                  <a href="#" target="_blank">Privacy and Accessibility</a>
                  <a href="#" target="_blank">Contact</a>
              </div>
            </footer>
        </div>
  );
}

export default MainLayout;
