import React, {useEffect, useState} from 'react';
import './App.css';
import useWebSocket from 'react-use-websocket';
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
import PowerSensorSelect from "./PowerSensorSelect";

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
    const [labels, setLabels] = useState<string[]>([])
    const [powerConsumption, setPowerConsumption] = useState<number[]>([])

    const {sendMessage, lastMessage, readyState} = useWebSocket(getWebsocketUrl(process.env.REACT_APP_API_URL || ""))
    useEffect(() => {
        if (lastMessage !== null) {
            const msg = JSON.parse(lastMessage.data)
            console.log(`${msg.entity_id} ${msg.state}${msg.attributes.unit_of_measurement}`)

            const time_formatted = new Date(msg.last_updated).toLocaleTimeString()
            const value = parseFloat(msg.state)

            setLabels(labels => [...labels, time_formatted])
            setPowerConsumption(powerConsumption => [...powerConsumption, value])
        }
    }, [lastMessage, setLabels, setPowerConsumption])

    const data = {
        labels: labels,
        datasets: [
            {
                label: 'Energie verbruik',
                data: powerConsumption,
                borderColor: 'rgba(68, 115, 158, 1)',
                backgroundColor: 'rgba(68, 115, 158, 0.5)',
            }
        ]
    }

    return (
        <div className="grid-x grid-padding-x grid-padding-y">
            <div className="medium-6 cell">
                <h1>Powermon</h1>
                <p>
                    Rechts kan je je verbruik zien. Hiervoor gebruiken we een sensor in Home Assistant die het
                    vermogen meet dat je op dit ogenblik gebruikt.
                </p>
                <p>
                    Je kan deze sensor hieronder kiezen. Een ideale sensor is
                    de <a href="https://www.home-assistant.io/integrations/dsmr/">integratie met de slimme meter</a>.
                    Dit is het exacte cijfer dat ook gebruikt wordt voor de berekening van je factuur.
                </p>
                <p>
                    Selecteer hieronder de juiste sensor. Je ziet hier enkel vermogensensoren in (kilo)watt, omdat deze
                    sensoren het vermogen meten. Andere sensoren meten je totale verbruik in (kilo)wattuur. Deze kunnen
                    niet rechtstreeks gebruikt worden om je piekverbruik te berekenen.
                </p>
                <PowerSensorSelect/>
            </div>
            <div className="medium-6 cell">
                <Line data={data}/>
            </div>
        </div>
    );
}

export default App
