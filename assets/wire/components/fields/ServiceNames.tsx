import {FieldRenderProps} from 'interfaces/configs';
import React from 'react';

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
export const ServiceNames = ({item}: FieldRenderProps) => {
    if (!item) return null;

    const services = item['service'] || [];

    if (!services) return null;

    const names: string[] = [];

    if (Array.isArray(services)) {
        names.push(...services.map(v => v.name ?? '').filter(Boolean));
    }
    else if (typeof services === 'string')
        names.push(services);

    return names.length > 0 ? <span style={{fontWeight: 'bold'}}>{names.join(', ')}</span> : null;
};
