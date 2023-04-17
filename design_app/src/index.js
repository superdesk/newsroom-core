import React from 'react';
import ReactDOM from 'react-dom';

import App from './components/App';

import '../../assets/styles/app.scss'; // Newshub - import of everything
import './assets/styles/_design_external-style.scss'; // Static file
// import './assets/styles/theme.css'; // CP Theme

ReactDOM.render(
  React.createElement(App),
  document.getElementById('root'),
);

// Check if hot reloading is enable. If it is, changes won't reload the page.
// This is related to webpack-dev-server and works on development only.
if (module.hot) {
  module.hot.accept();
}
