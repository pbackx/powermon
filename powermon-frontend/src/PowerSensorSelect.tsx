import React, {useEffect, useState} from "react";

interface Sensor {
    entity_id: string
    attributes: {
        friendly_name: string
    }
}

function PowerSensorSelect() {
    const [selectedSensor, setSelectedSensor] = useState<string | undefined>(undefined)
    const [sensors, setSensors] = useState<Sensor[]>([])
    const [disabled, setDisabled] = useState<boolean>(false)

    useEffect(() => {
        window.fetch((process.env.REACT_APP_API_URL || "") + "sensor")
            .then(response => response.json())
            .then(data => setSelectedSensor(data.selected_sensor))
            .then(() => window.fetch((process.env.REACT_APP_API_URL || "") + "sensor/list"))
            .then(response => response.json())
            .then(data => setSensors(data))
            .catch(error => console.log(`Error: ${error}`))
    }, [setSensors, setSelectedSensor])

    function selectNewSensor(event: React.ChangeEvent<HTMLSelectElement>) {
        setDisabled(true)
        const newSelectedSensor= event.currentTarget.value
        fetch((process.env.REACT_APP_API_URL || "") + "sensor", {
            method: "POST",
            mode: "cors",
            body: JSON.stringify({selected_sensor: newSelectedSensor})})
            .then(response => response.json())
            .then(console.log)
            .catch(error => console.log(`Error: ${error}`))
            .finally(() => setDisabled(false))
    }

    return (
            <select value={selectedSensor}
                    onChange={selectNewSensor}
                    disabled={disabled}
            >
            {sensors.map(sensor =>
                <option
                    key={sensor.entity_id}
                    value={sensor.entity_id}
                >{sensor.attributes.friendly_name}
                </option>)
            }
        </select>
    )
}

export default PowerSensorSelect