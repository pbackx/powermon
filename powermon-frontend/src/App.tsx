import React, {useEffect, useState} from 'react';
import logo from './logo.svg';
import './App.css';

function App() {
  const [message, setMessage] = useState("loading...");

  console.log(process.env.REACT_APP_API_URL)

  useEffect(() => {
    window.fetch(process.env.REACT_APP_API_URL || "")
        .then(response => response.json())
        .then(data => setMessage(data.message));
    // note: don't forget about error handling, see example on https://reactjs.org/docs/faq-ajax.html
  });

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          {message}
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
