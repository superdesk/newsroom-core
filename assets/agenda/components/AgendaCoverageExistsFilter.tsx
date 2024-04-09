import React from 'react';
import {memoize} from 'lodash';

import {gettext, getConfig} from 'utils';
import {AgendaDropdown} from './AgendaDropdown';

type ICoverageStatusOptionValue = 'planned' | 'not planned' | 'may be' | 'not intended' | 'completed';

interface IProps {
    toggleFilter(field: string, value?: ICoverageStatusOptionValue): void;
    activeFilter: {coverage_status?: Array<ICoverageStatusOptionValue>};
}

interface ICoverageStatusOptionConfig {
    enabled: boolean;
    index: number;
    option_label: string;
    button_label: string;
}

type ICoverageStatusFilterConfig = {[value in ICoverageStatusOptionValue]: ICoverageStatusOptionConfig};

export const agendaCoverageStatusFilter = {
    label: gettext('Any coverage status'),
    field: 'coverage_status',
    nestedField: 'coverage_status',
};

export function getActiveFilterLabel(
    filter: {label: string; field: string},
    activeFilter?: {
        coverage_status?: Array<ICoverageStatusOptionValue>;
        [field: string]: any;
    }
) {
    const config: ICoverageStatusFilterConfig = getConfig('coverage_status_filter');

    return activeFilter?.coverage_status?.[0] != null ?
        config[activeFilter.coverage_status[0]].button_label :
        filter.label;
}

const getCoverageStatusOptions = memoize<() => Array<[ICoverageStatusOptionValue, ICoverageStatusOptionConfig]>>(() => {
    const config: ICoverageStatusFilterConfig = getConfig('coverage_status_filter');
    const enabledOptionValues: Array<ICoverageStatusOptionValue> = [
        'planned',
        'may be',
        'not intended',
        'not planned',
        'completed',
    ];

    return enabledOptionValues
        .filter((optionValue) => config[optionValue]?.enabled == true)
        .sort((optionA, optionB) => config[optionA].index - config[optionB].index)
        .map((optionValue) => ([optionValue, config[optionValue]]));
});

function AgendaCoverageExistsFilter({toggleFilter, activeFilter}: IProps) {
    return (
        <AgendaDropdown
            filter={agendaCoverageStatusFilter}
            activeFilter={activeFilter}
            toggleFilter={toggleFilter}
            getFilterLabel={getActiveFilterLabel}
            optionLabel={gettext('Coverage')}
            hideLabelOnMobile
            resetOptionLabel={gettext('Clear selection')}
            dropdownMenuHeader={gettext('Coverage status')}
        >
            {getCoverageStatusOptions().map(([value, config]) => (
                <button
                    key={`coverage-${value}`}
                    className="dropdown-item"
                    onClick={() => toggleFilter(agendaCoverageStatusFilter.field, value)}
                >
                    {config.option_label}
                </button>
            ))}
        </AgendaDropdown>
    );
}

export default AgendaCoverageExistsFilter;
