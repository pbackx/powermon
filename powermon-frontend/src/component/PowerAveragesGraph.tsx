import PowerValue from "../model/PowerValue"
import React, {CSSProperties} from "react"
import {Line} from "react-chartjs-2"
import {ChartOptions} from "chart.js"

interface PowerAveragesGraphProps {
    powerAverages: PowerValue[]
}
export default function PowerAveragesGraph(props: PowerAveragesGraphProps) {
    const powerAverages = props.powerAverages

    const data = {
        labels: powerAverages.map(pm => pm.timestamp.toLocaleDateString()),
        datasets: [
            {
                label: 'Kwartier gemiddelde',
                data: powerAverages.map(pm => pm.power),
                borderColor: 'rgba(68, 115, 158, 1)',
                backgroundColor: 'rgba(68, 115, 158, 0.5)',
                tension: 0.4,
            }
        ]
    }

    const options: ChartOptions<"line"> = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        }
    }

    const style: CSSProperties = {
        position: "relative",
        height: "15rem",
    }

    return (
        <div style={style}>
            <Line data={data} options={options}/>
        </div>
    )
}