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
    resetOptionLabel?: string;
}

export function AgendaDropdown({
    filter,
    optionLabel,
    activeFilter,
    toggleFilter,
    children,
    getFilterLabel,
    borderless,
    resetOptionLabel,
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
            {isActive ? (
                <>
                    <button
                        type='button'
                        className='dropdown-item'
                        onClick={() => toggleFilter(filter.field, null)}
                    >
                        {resetOptionLabel ?? gettext(filter.label)}
                    </button>
                    <div className='dropdown-divider'></div>
                </>
            ) : null}
            {children}
        </Dropdown>
    );
}
