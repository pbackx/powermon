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
} from 'chart.js'
import PowerSensorSelect from "./component/PowerSensorSelect"
import PowerValue from "./model/PowerValue"
import PowerReadingsGraph from "./component/PowerReadingsGraph"
import PowerAveragesGraph from "./component/PowerAveragesGraph"
import PowerPeakGraph from "./component/PowerPeakGraph";

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
    const [powerReadings, setPowerReadings] = useState<PowerValue[]>([]);
    const [powerAverages, setPowerAverages] = useState<PowerValue[]>([]);
    const [powerPeaks, setPowerPeaks] = useState<PowerValue[]>([]);
    const [averageYearlyPeak, setAverageYearlyPeak] = useState<number>(0);

    const {lastMessage} = useWebSocket(getWebsocketUrl(process.env.REACT_APP_API_URL || ""))
    useEffect(() => {
        if (lastMessage !== null) {
            const updatesRaw = JSON.parse(lastMessage.data) as any[]
            const updates = updatesRaw.map((update) => ({
                timestamp: new Date(update.timestamp),
                power: update.power as number,
                type: update.type
            }))
            const readingUpdates = updates.filter(update => update.type === "reading")
            if (readingUpdates.length > 0) {
                const oneHourAgo = new Date(new Date().getTime() - 60 * 60 * 1000)
                setPowerReadings(powerReadings =>
                    mergePowerValues([...powerReadings, ...readingUpdates]
                        .filter(pm => pm.timestamp > oneHourAgo))
                )
            }
            const averageUpdates = updates.filter(update => update.type === "average")
            if (averageUpdates.length > 0) {
                const oneMonthAgo = new Date(new Date().getTime() - 30 * 24 * 60 * 60 * 1000)
                setPowerAverages(powerAverages =>
                    mergePowerValues([...powerAverages, ...averageUpdates]
                        .filter(pm => pm.timestamp > oneMonthAgo))
                )
            }
            const peakUpdates = updates.filter(update => update.type === "peak")
            if (peakUpdates.length > 0) {
                const oneYearAgo = new Date(new Date().getTime() - 365 * 24 * 60 * 60 * 1000)
                setPowerPeaks(powerPeaks =>
                    mergePowerValues([...powerPeaks, ...peakUpdates]
                        .filter(pm => pm.timestamp > oneYearAgo))
                )
            }
            const yearAverage = updates.filter(update => update.type === "year_average")
            if (yearAverage.length > 0) {
                setAverageYearlyPeak(yearAverage[yearAverage.length - 1].power)
            }
        }
    }, [lastMessage])

    function mergePowerValues(powerValues: PowerValue[]) {
        const powerValuesByTimestamp = powerValues.reduce((acc, pv) => {
            acc[pv.timestamp.getTime()] = pv
            return acc
        }, {} as Record<number, PowerValue>)
        return Object.values(powerValuesByTimestamp)
    }


    return (
        <div className="grid-container">
            <div className="grid-x grid-padding-x grid-padding-y">
                <div className="cell">
                    <h1>Powermon</h1>
                </div>
                <div className="medium-6 cell">
                    <p>
                        Rechts op de grafiek, zie je je verbruik van het afgelopen uur. Hiervoor gebruiken we een sensor
                        in Home Assistant die het
                        vermogen meet dat je op dit ogenblik gebruikt.
                    </p>
                    <p>
                        Je kan deze sensor hieronder kiezen. Een ideale sensor is
                        de <a href="https://www.home-assistant.io/integrations/dsmr/">integratie met de slimme meter</a>.
                        Dit is het exacte cijfer dat ook gebruikt wordt voor de berekening van je factuur.
                    </p>
                    <p>
                        Selecteer hieronder de juiste sensor. Je ziet hier enkel vermogensensoren in (kilo)watt, omdat
                        deze
                        sensoren het vermogen meten. Andere sensoren meten je totale verbruik in (kilo)wattuur. Deze
                        kunnen
                        niet rechtstreeks gebruikt worden om je piekverbruik te berekenen.
                    </p>
                    <PowerSensorSelect/>
                </div>
                <div className="medium-6 cell">
                    <PowerReadingsGraph powerReadings={powerReadings}/>
                </div>
                <div className="medium-8 cell">
                    <PowerAveragesGraph powerAverages={powerAverages}/>
                </div>
                <div className="medium-4 cell">
                    <p>
                        Op de volgende grafiek zie je jouw kwartiervermogen van de voorbij maand.
                    </p>
                    <p>
                        Dat is het gemiddelde verbruik dat je tijdens
                        elk kwartier van de afgelopen maand hebt gehad.
                    </p>
                    <p>
                        Heb je bijvoorbeeld een kwartier lang een toestel van 1000W gebruikt, dan zal het
                        kwartiervermogen
                        1000W zijn. Heb je 5 minuten lang een toestel van 1000W gebruikt en daarna totaal niks meer, dan
                        zal het vermogen 1000/3 of ongeveer 333W zijn.
                    </p>
                </div>
                <div className="medium-4 cell">
                    <p>
                        Vervolgens bepalen we op basis van dit kwartiervermogen je maandpieken van het laatste jaar.
                    </p>
                    <p>
                        Een maandpiek is het grootste
                        kwartiervermogen dat je tijdens een maand hebt gehad.
                    </p>
                    <p>
                        Aangezien dit pas op het einde van de maand gekend is, zal het even duren voor je hier
                        data ziet verschijnen.
                    </p>
                </div>
                <div className="medium-8 cell">
                    <PowerPeakGraph powerPeaks={powerPeaks}/>
                </div>
                <div className="medium-6 cell grid-x align-center-middle">
                    <h1>{averageYearlyPeak} W</h1>
                </div>
                <div className="medium-6 cell">
                    <p>
                        De laatste stap is op basis van de voorbije twaalf maandpieken je piekvermogen voor het jaar te
                        berekenen. Dit is het gemiddelde van de twaalf maandpieken.
                    </p>
                    <p>
                        Een onderdeel van je elektriciteitsfactuur zal afhankelijk zijn van dit piekvermogen. Hoe hoger
                        dit
                        is is, hoe meer. Dit is sterk afhankelijk van je situatie en je kan dit best simuleren, maar een
                        richtprijs is dat je per kW extra piek ongeveer 40 euro per jaar extra betaalt.
                    </p>
                </div>
                <div className="medium-12 cell">
                    <h2>Begrippenlijst en verdere uitleg</h2>
                    <dl>
                        <dt>Vermogen versus verbruik</dt>
                        <dd>Het is heel eenvoudig om deze beide begrippen te verwarren. Het vermogen dat je op
                            toestellen
                            vindt
                            is steeds aangeduid in watt (W) of kilowatt (kW = 1000 W). Het duidt aan hoeveel energie een
                            toestel maximaal
                            per seconde zal gebruiken. Het verbruik is hoeveel energie een toestel tijdens een bepaalde
                            periode
                            heeft gebruikt. Bijvoorbeeld, staat je microgolf die 1000W verbruik 15 minuten aan, dan zal
                            die
                            dat uur 1000W x 15min / 60min/uur = 250Wh verbruikt hebben. Het grootste deel van je
                            elektriciteitsrekening
                            is afhankelijk van je verbruik. Het capaciteitstarief voegt nu ook een onderdeel toe waarbij
                            je
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
        </div>
    );
}

export default App
