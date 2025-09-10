import React from 'react';

type Named = { name?: string };

export interface IServiceNamesProps {
    value?: Named[] | string | null;
    styles?: React.CSSProperties;
}

/**
 * ServiceNames component
 *
 * Renders a list of names as a comma-separated string inside a <span>.
 * - If `value` is an array of objects with a `name` property, it extracts each `name` and joins them.
 * - If `value` is a string, it displays the string directly.
 *
 * Example outputs:
 * - `[{ name: "Reuters" }, { name: "AP" }]` → `"Reuters, AP"`
 * - `"BBC"` → `"BBC"`
 */
export const ServiceNames = ({value, styles}: IServiceNamesProps) => {
    if (!value) return null;

    const names: string[] = [];

    if (Array.isArray(value)) {
        names.push(...value.map(v => v.name ?? '').filter(Boolean));
    }
    else if (typeof value === 'string')
        names.push(value);

    return names.length > 0 ? <span style={styles}>{names.join(', ')}</span> : null;
};
