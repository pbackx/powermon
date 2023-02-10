import PowerValue from "../model/PowerValue";
import {Line} from "react-chartjs-2";
import {ChartData, ChartOptions} from "chart.js";
import {CSSProperties} from "react";

interface PowerPeakGraphProps {
    powerPeaks: PowerValue[]
}

export default function PowerPeakGraph(props: PowerPeakGraphProps) {
    const powerPeaks = props.powerPeaks;

    const data: ChartData<"line"> = {
        labels: powerPeaks.map(pm => pm.timestamp.toLocaleDateString()),
        datasets: [
            {
                label: 'Maandpiek',
                data: powerPeaks.map(pm => pm.power),
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