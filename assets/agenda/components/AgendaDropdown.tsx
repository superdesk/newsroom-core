import React from 'react';
import {gettext} from 'utils';
import {Dropdown} from '../../components/Dropdown';

interface IProps {
    filter: any;
    optionLabel?: string;
    activeFilter?: any;
    toggleFilter: (filedName: string, value: any) => void;
    getFilterLabel?: (filter: string, activeFilter: string, isActive: boolean) => string;
    children?: any;
    borderless?: boolean;
}

export function AgendaDropdown({
    filter,
    optionLabel,
    activeFilter,
    toggleFilter,
    children,
    getFilterLabel,
    borderless,
}: IProps) {

    const isActive = activeFilter[filter.field];
    const getActiveFilterLabel = getFilterLabel != null ?
        getFilterLabel :
        (filter: any, activeFilter: any, isActive: any) => {
            return isActive ? gettext(activeFilter[filter.field][0]) : gettext(filter.label);
        };

    return (
        <Dropdown
            borderless={borderless}
            isActive={isActive}
            icon={filter.icon}
            optionLabel={optionLabel}
            label={getActiveFilterLabel(filter, activeFilter, isActive)}
        >
            <button
                type='button'
                className='dropdown-item'
                onClick={() => toggleFilter(filter.field, null)}
            >
                {gettext(filter.label)}
            </button>
            <div className='dropdown-divider'></div>
            {children}
        </Dropdown>
    );
}
