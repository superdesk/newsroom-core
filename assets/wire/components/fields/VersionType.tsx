import React from 'react';
import {gettext} from 'utils';

interface IProps {
    value: string
}

export function VersionType({value}: IProps) {
    return (
        <span>{gettext('Version type: {{version}}', {version: value})}</span>
    );
}

