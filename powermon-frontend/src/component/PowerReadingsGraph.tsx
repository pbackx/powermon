import {Line} from 'react-chartjs-2'
import PowerValue from "../model/PowerValue"
import {ChartData, ChartOptions} from "chart.js"
import {CSSProperties} from "react";

interface PowerReadingsGraphProps {
    powerReadings: PowerValue[]
}

export default function PowerReadingsGraph(props: PowerReadingsGraphProps) {
    const powerReadings = props.powerReadings

    const data: ChartData<"line"> = {
        labels: powerReadings.map(pm => pm.timestamp.toLocaleTimeString()),
        datasets: [
            {
                label: 'Energie verbruik',
                data: powerReadings.map(pm => pm.power),
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
        height: "20rem",
    }

    return (
        <div style={style}>
            <Line data={data} options={options}/>
        </div>
    )
}