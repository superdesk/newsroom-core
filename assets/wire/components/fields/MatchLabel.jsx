import * as React from 'react';
import {gettext} from 'utils';

export function MatchLabel() {
    return (
        <span className={'label label-rounded label--success mr-2 mb-1'}>
            {gettext('MATCH')}
        </span>
    );
}
