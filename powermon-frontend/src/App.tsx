import React, {useEffect, useState} from 'react';
import './App.css';
import useWebSocket, {ReadyState} from 'react-use-websocket';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import {Line} from 'react-chartjs-2';

function getWebsocketUrl(url: string) {
    let websocketUrl
    if (url.startsWith("http://")) {
        websocketUrl = url.replace(/^http/, "ws")
    } else {
        const l = window.location
        websocketUrl = "ws://" + l.host + l.pathname + url.replace(/^\.\//, "")
    }

    if (websocketUrl.endsWith("/")) {
        return websocketUrl + "ws"
    } else {
        return websocketUrl + "/ws"
    }
}

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

function App() {
    const [message, setMessage] = useState("loading...")
    const [labels, setLabels] = useState<string[]>([])
    const [powerConsumption, setPowerConsumption] = useState<number[]>([])

    const {sendMessage, lastMessage, readyState} = useWebSocket(getWebsocketUrl(process.env.REACT_APP_API_URL || ""))
    useEffect(() => {
        if (lastMessage !== null) {
            const msg = JSON.parse(lastMessage.data)
            console.log(`${msg.entity_id} ${msg.state}${msg.attributes.unit_of_measurement}`)

            const time_formatted = new Date(msg.last_updated).toLocaleTimeString()
            const value = parseFloat(msg.state)

            setLabels([...labels, time_formatted])
            setPowerConsumption([...powerConsumption, value])
        }
    }, [lastMessage])

    useEffect(() => {
        window.fetch(process.env.REACT_APP_API_URL || "")
            .then(response => response.json())
            .then(data => setMessage(data.message))
            .catch(error => setMessage(`Error: ${error}`))
    }, [setMessage])

    const connectionStatus = {
        [ReadyState.CONNECTING]: 'Connecting',
        [ReadyState.OPEN]: 'Open',
        [ReadyState.CLOSING]: 'Closing',
        [ReadyState.CLOSED]: 'Closed',
        [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
    }[readyState]

    const data = {
        labels: labels,
        datasets: [
            {
                label: 'Power consumption',
                data: powerConsumption,
                borderColor: 'rgba(68, 115, 158, 1)',
                backgroundColor: 'rgba(68, 115, 158, 0.5)',
            }
        ]
    }

    return (
        <div className="App">
            <header className="App-header">
                <p>
                    {message}
                </p>
                <p>
                    WS connection status: {connectionStatus}
                </p>
            </header>
            <Line data={data}/>
        </div>
    );
}

export default App
