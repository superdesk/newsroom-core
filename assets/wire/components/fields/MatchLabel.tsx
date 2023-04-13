import {gettext} from 'assets/utils';
import * as React from 'react';

export function MatchLabel() {
    return (
        <span className={'label label-rounded label--green me-2 mb-1'}>
            {gettext('MATCH')}
        </span>
    );
}
