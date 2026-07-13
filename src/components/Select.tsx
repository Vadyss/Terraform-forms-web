interface SelectProps {
    value: string | number
    onChange: (value: string) => void
    options: { value: string | number; label: string }[]
    label: string
}

export function Select( {value, onChange, options, label}: SelectProps) {
    return (
        <label>
            {label}
            <select value={value} onChange={(e) => onChange(e.target.value)}>
            {options.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
            </select>
        </label>
        );
}