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

interface PowerValue {
    timestamp: Date,
    power: number,
    type: string,
}

function App() {
    const [powerReadings, setPowerReadings] = useState<PowerValue[]>([]);
    const [powerAverages, setPowerAverages] = useState<PowerValue[]>([]);
    const [powerPeaks, setPowerPeaks] = useState<PowerValue[]>([]);

    const {lastMessage} = useWebSocket(getWebsocketUrl(process.env.REACT_APP_API_URL || ""))
    useEffect(() => {
        if (lastMessage !== null) {
            const updatesRaw = JSON.parse(lastMessage.data) as any[]
            const updates = updatesRaw.map((update) => ({
                timestamp: new Date(update.timestamp),
                power: update.power,
                type: update.type
            }))
            const readingUpdates = updates.filter(update => update.type === "reading")
            if (readingUpdates.length > 0) {
                const oneHourAgo = new Date(new Date().getTime() - 60 * 60 * 1000)
                setPowerReadings(powerReadings =>
                    [...powerReadings, ...readingUpdates]
                        .filter(pm => pm.timestamp > oneHourAgo)
                )
            }
            const averageUpdates = updates.filter(update => update.type === "average")
            if (averageUpdates.length > 0) {
                //TODO remove duplicate timestamps
                const oneMonthAgo = new Date(new Date().getTime() - 30 * 24 * 60 * 60 * 1000)
                setPowerAverages(powerAverages =>
                    [...powerAverages, ...averageUpdates]
                        .filter(pm => pm.timestamp > oneMonthAgo)
                )
            }
            const peakUpdates = updates.filter(update => update.type === "peak")
            if (peakUpdates.length > 0) {
                //TODO remove duplicate timestamps
                const oneYearAgo = new Date(new Date().getTime() - 365 * 24 * 60 * 60 * 1000)
                setPowerPeaks(powerPeaks =>
                    [...powerPeaks, ...peakUpdates]
                        .filter(pm => pm.timestamp > oneYearAgo)
                )
            }
        }
    }, [lastMessage])

    const powerReadingsGraph = {
        labels: powerReadings.map(pm => pm.timestamp.toLocaleTimeString()),
        datasets: [
            {
                label: 'Energie verbruik',
                data: powerReadings.map(pm => pm.power),
                borderColor: 'rgba(68, 115, 158, 1)',
                backgroundColor: 'rgba(68, 115, 158, 0.5)',
            }
        ]
    }
    const powerAveragesGraph = {
        labels: powerAverages.map(pm => pm.timestamp.toLocaleDateString()),
        datasets: [
            {
                label: 'Kwartier gemiddelde',
                data: powerAverages.map(pm => pm.power),
                borderColor: 'rgba(68, 115, 158, 1)',
                backgroundColor: 'rgba(68, 115, 158, 0.5)',
            }
        ]
    }
    const powerPeakGraph = {
        labels: powerPeaks.map(pm => pm.timestamp.toLocaleDateString()),
        datasets: [
            {
                label: 'Maandpiek',
                data: powerPeaks.map(pm => pm.power),
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
                <Line data={powerReadingsGraph}/>
            </div>
            <div className="medium-8 cell">
                <Line data={powerAveragesGraph}/>
            </div>
            <div className="medium-4 cell">
                <p>
                    Op de volgende grafiek zie je jouw kwartiervermogen. Dat is het gemiddelde verbruik dat je tijdens
                    het kwartier hebt gehad.
                </p>
                <p>
                    Heb je bijvoorbeeld een kwartier lang een toestel van 1000W gebruikt, dan zal het kwartiervermogen
                    1000W zijn. Heb je 5 minuten lang een toestel van 1000W gebruikt en daarna totaal niks meer, dan
                    zal het vermogen 1000/3 of ongeveer 333W zijn.
                </p>
            </div>
            <div className="medium-4 cell">
                <p>
                    Vervolgens bepalen we op basis van dit kwartiervermogen je maandpiek. Dat is het grootste
                    kwartiervermogen dat je tijdens een maand hebt gehad.
                </p>
            </div>
            <div className="medium-8 cell">
                <Line data={powerPeakGraph}/>
            </div>
            <div className="medium-6 cell">
                <p>TODO add graph</p>
            </div>
            <div className="medium-6 cell">
                <p>
                    De laatste stap is op basis van de voorbije twaalf maandpieken je piekvermogen voor het jaar te
                    berekenen. Dit is het gemiddelde van de twaalf maandpieken.
                </p>
                <p>
                    Een onderdeel van je elektriciteitsfactuur zal afhankelijk zijn van dit piekvermogen. Hoe hoger dit
                    is is, hoe meer. Dit is sterk afhankelijk van je situatie en je kan dit best simuleren, maar een
                    richtprijs is dat je per kW extra piek ongeveer 40 euro per jaar extra betaalt.
                </p>
                <p>
                    TODO: aanvullen met extra gegevens en een aantal simulaties.
                </p>
            </div>
            <div className="medium-12 cell">
                <h2>Begrippenlijst en verdere uitleg</h2>
                <dl>
                    <dt>Vermogen versus verbruik</dt>
                    <dd>Het is heel eenvoudig om deze beide begrippen te verwarren. Het vermogen dat je op toestellen
                        vindt
                        is steeds aangeduid in watt (W) of kilowatt (kW = 1000 W). Het duidt aan hoeveel energie een
                        toestel maximaal
                        per seconde zal gebruiken. Het verbruik is hoeveel energie een toestel tijdens een bepaalde
                        periode
                        heeft gebruikt. Bijvoorbeeld, staat je microgolf die 1000W verbruik 15 minuten aan, dan zal die
                        dat uur 1000W x 15min / 60min/uur = 250Wh verbruikt hebben. Het grootste deel van je
                        elektriciteitsrekening
                        is afhankelijk van je verbruik. Het capaciteitstarief voegt nu ook een onderdeel toe waarbij je
                        moet
                        betalen voor het maximale vermogen dat je verbruikt.
                    </dd>
                    <dt>Bronnen</dt>
                    <dd>Voor het opstellen van deze pagina werden de volgende bronnen gebruikt:
                        <ul>
                            <li><a href="https://www.vreg.be/nl/faq/nieuwe-nettarieven-2023">Vragenlijst nieuwe
                                nettarieven VREG</a></li>
                        </ul>
                    </dd>
                </dl>
            </div>
        </div>
    );
}

export default App
