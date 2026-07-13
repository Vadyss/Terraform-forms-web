interface ToggleProps {
    checked: boolean;
    onChange: (value: boolean) => void;
    label: string;
}

export function Toggle( {checked, onChange, label }: ToggleProps) {

    return (
        <label className="toggle">
            <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
            <span className="track"></span>
            {label}
        </label>
    )
}