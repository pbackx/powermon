import React, {useEffect, useState} from 'react';
import logo from './logo.svg';
import './App.css';
import useWebSocket, {ReadyState} from 'react-use-websocket';

function getWebsocketUrl(url: string) {
  return url.replace(/^http/, "ws") + "ws"
}

function App() {
  const [message, setMessage] = useState("loading...")

  const { sendMessage, lastMessage, readyState } = useWebSocket(getWebsocketUrl(process.env.REACT_APP_API_URL || ""))
  useEffect(() => {
    if (lastMessage !== null) {
      console.log(JSON.parse(lastMessage.data))
    }
  }, [lastMessage])

  useEffect(() => {
    window.fetch(process.env.REACT_APP_API_URL || "")
        .then(response => response.json())
        .then(data => setMessage(data.message))
    // note: don't forget about error handling, see example on https://reactjs.org/docs/faq-ajax.html
  }, [setMessage])

  const connectionStatus = {
    [ReadyState.CONNECTING]: 'Connecting',
    [ReadyState.OPEN]: 'Open',
    [ReadyState.CLOSING]: 'Closing',
    [ReadyState.CLOSED]: 'Closed',
    [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
  }[readyState]

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          {message}
        </p>
        <p>
            WS connection status: {connectionStatus}
        </p>
      </header>
    </div>
  );
}

export default App
